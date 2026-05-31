"""
utils/image_pipeline.py
Full pipeline for a single paper:
  1. Extract all meaningful images from the PDF using PyMuPDF + Pillow.
     Each image is saved as a PNG on disk AND converted to base64 in memory.
  2. Send that base64 directly to Gemini Vision — no re-reading the file.
     Uses gemini_direct_call from llm_manager so API keys are rotated on
     quota errors exactly like the rest of the pipeline.
  3. Attach the explanation to the image dict.
  4. Cache the result (path + explanation, no b64) so the same paper is
     never processed again.

Public entry point:
    get_or_create_images(pdf_path, available_keys, exhausted_keys=None, paper_id=None)
    → (images, updated_available_keys, updated_exhausted_keys)

    images: [{page, index, filename, image_path, width, height, explanation}]

API key rules:
  Demo mode : pass [os.getenv("GEMINI_API_KEY_1")]
  Live mode : pass state["available_api_keys"] + state["exhausted_api_keys"]
"""

import io
import json
import time
import base64
from pathlib import Path

import fitz          # PyMuPDF
from PIL import Image


# ── Config ────────────────────────────────────────────────────────────────────

OUTPUT_DIR     = Path("extracted_images")      # where PNGs are saved
CACHE_DIR      = Path("extracted_assets/cache")
MIN_IMAGE_SIZE = 100   # skip images smaller than 100×100 px (logos, bullets, etc.)

# Explanation values that indicate a stale / errored cache entry
_STALE_MARKERS = [
    "api error", "could not generate", "error 403", "error 400",
    "error 500", "error 503", "unavailable",
]


def _explanation_is_stale(text: str) -> bool:
    """Return True when an explanation looks like an old error string."""
    low = (text or "").lower()
    return any(m in low for m in _STALE_MARKERS)


# ── Step 1: Extract images ────────────────────────────────────────────────────

def extract_images_from_pdf(pdf_path):
    """
    Extract all meaningful raster images from a PDF using PyMuPDF + Pillow.

    Each image is:
      - saved as a PNG in extracted_images/
      - converted to base64 IN MEMORY (no re-read needed later)

    Returns a list of dicts:
        {page, index, filename, image_path, width, height, b64_data}
    b64_data is used directly for the Gemini API call.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc       = fitz.open(pdf_path)
    extracted = []

    for page_num in range(len(doc)):
        page       = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]

            # Pull raw image bytes from the PDF
            base_image  = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Open with Pillow to get dimensions and normalise format
            pil_img        = Image.open(io.BytesIO(image_bytes))
            width, height  = pil_img.size

            # Skip decorative images that are too small
            if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
                continue

            # Convert to RGB so everything is a consistent PNG
            if pil_img.mode not in ("RGB", "L"):
                pil_img = pil_img.convert("RGB")

            # Save to disk
            filename  = f"page{page_num + 1}_img{img_index + 1}.png"
            save_path = OUTPUT_DIR / filename
            pil_img.save(str(save_path), "PNG")

            # Encode to base64 from the same in-memory buffer — no file re-read
            buffer = io.BytesIO()
            pil_img.save(buffer, format="PNG")
            b64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

            extracted.append({
                "page":       page_num + 1,
                "index":      img_index + 1,
                "filename":   filename,
                "image_path": str(save_path),   # consistent with rag/extractor and UI
                "width":      width,
                "height":     height,
                "b64_data":   b64_data,          # ready to send to Gemini directly
            })

    doc.close()
    return extracted


# ── Step 2: Explain with Gemini Vision ───────────────────────────────────────

def explain_image(b64_data, page, available_keys, exhausted_keys):
    """
    Send the already-computed base64 image data to Gemini Vision.
    Uses b64_data directly — no file re-read, no re-encoding.

    API keys are rotated on quota errors via gemini_direct_call, matching
    the same fallback pattern used by the LangGraph agents.

    Returns (explanation_text, updated_available_keys, updated_exhausted_keys).
    """
    from utils.llm_manager import gemini_direct_call, AllKeysExhausted

    parts = [
        {
            "inline_data": {
                "mime_type": "image/png",
                "data":      b64_data,   # already base64-encoded from extraction step
            }
        },
        {
            "text": (
                "You are analyzing a figure from a research paper. "
                "Please explain this image clearly and concisely:\n"
                "1. What type of figure is this? (chart, diagram, graph, table, photo, etc.)\n"
                "2. What is the main subject or finding shown?\n"
                "3. What are the key details, labels, or trends visible?\n"
                "4. What conclusion or insight does this figure convey?\n"
                "Keep the explanation informative but under 150 words."
            )
        },
    ]
    try:
        text, avail, exh = gemini_direct_call(
            available_keys, exhausted_keys, parts,
            temperature=0.2, max_tokens=350,
        )
        return text, avail, exh
    except AllKeysExhausted as e:
        return (
            "Explanation unavailable — API keys exhausted or unauthorised. "
            "Please provide a fresh key to regenerate.",
            e.available,
            e.exhausted,
        )
    except Exception as e:
        return (
            f"Explanation unavailable ({type(e).__name__}). "
            "The image was extracted successfully.",
            list(available_keys),
            list(exhausted_keys),
        )


# ── Step 3: Cache helpers ─────────────────────────────────────────────────────

def _load_cache(paper_id):
    """
    Load cached image results for a paper.
    Returns a list of image dicts (without b64_data) or None if not cached.
    Automatically invalidates caches that contain stale error explanations.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{paper_id}_images.json"
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            # Invalidate if any explanation contains an old error string
            if any(_explanation_is_stale(item.get("explanation", "")) for item in data):
                cache_file.unlink(missing_ok=True)
                return None
            return data
    except Exception:
        pass
    return None


def _save_cache(paper_id, images):
    """
    Save image results to cache.
    Strips b64_data before saving — the PNG files are on disk and can be
    re-read if the base64 is ever needed again.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{paper_id}_images.json"

    # Save only the fields needed for display — skip the large b64_data
    to_save = []
    for img in images:
        to_save.append({
            "page":        img["page"],
            "index":       img["index"],
            "filename":    img["filename"],
            "image_path":  img["image_path"],
            "width":       img["width"],
            "height":      img["height"],
            "explanation": img.get("explanation", ""),
        })

    try:
        with open(cache_file, "w") as f:
            json.dump(to_save, f, indent=2)
    except Exception:
        pass   # Non-fatal


# ── Public entry point ────────────────────────────────────────────────────────

def get_or_create_images(pdf_path, available_keys, exhausted_keys=None, paper_id=None):
    """
    Full image pipeline for one paper. Call this from anywhere.

    available_keys / exhausted_keys follow the same convention as
    invoke_with_fallback: keys are rotated on quota errors and moved to
    exhausted_keys.

    Returns (images, updated_available_keys, updated_exhausted_keys).

    Cache hit  → instant return, no extraction, no API calls.
    Cache miss → extracts images, calls Gemini Vision for each one,
                 saves PNGs to extracted_images/, saves cache JSON.

    paper_id: short stable string used as the cache key.
              Falls back to the PDF filename stem if not provided.
    """
    if exhausted_keys is None:
        exhausted_keys = []

    if not paper_id:
        paper_id = Path(pdf_path).stem[:40].replace(" ", "_").lower()

    # Fast path: return from cache
    cached = _load_cache(paper_id)
    if cached is not None:
        return cached, list(available_keys), list(exhausted_keys)

    # Extract all images (saves PNGs, computes b64_data in memory)
    images = extract_images_from_pdf(pdf_path)

    avail = list(available_keys)
    exh   = list(exhausted_keys)

    # Explain each image using the b64_data computed during extraction
    for i, img in enumerate(images):
        img["explanation"], avail, exh = explain_image(
            img["b64_data"], img["page"], avail, exh
        )
        # Gemini free tier: ~15 requests per minute
        if i < len(images) - 1:
            time.sleep(4)

    # Save to cache (b64_data stripped — PNGs are on disk)
    _save_cache(paper_id, images)

    return images, avail, exh

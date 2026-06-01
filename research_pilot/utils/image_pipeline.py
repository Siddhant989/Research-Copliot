import io
import os
import json
import time
import base64
import requests
from pathlib import Path

import fitz          # PyMuPDF
from PIL import Image
from dotenv import load_dotenv


load_dotenv(override=True)



# ── Config ────────────────────────────────────────────────────────────────────

OUTPUT_DIR     = Path("extracted_images")      # where PNGs are saved
CACHE_DIR      = Path("extracted_assets/cache")
MIN_IMAGE_SIZE = 100   # skip images smaller than 100×100 px (logos, bullets, etc.)

_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:generateContent?key={key}"
)

# Stale error strings that indicate a cache built by old, broken code
_STALE_MARKERS = [
    "api error", "could not generate", "error 403", "error 400",
    "error 500", "error 503",
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
                "image_path": str(save_path),
                "width":      width,
                "height":     height,
                "b64_data":   b64_data,
            })

    doc.close()
    return extracted


# ── Step 2: Explain with Gemini Vision ───────────────────────────────────────

def explain_image(b64_data, page):
    """
    Send the already-computed base64 image data to Gemini Vision.

    API keys are read from GOOGLE_API_KEY_* environment variables.
    Tries every key × every model until one succeeds.

    Returns an explanation string.
    """
    models = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    api_list = [
        value
        for key, value in os.environ.items()
        if key.startswith("GOOGLE_API_KEY_")
    ]

    prompt_text = (
        "You are analyzing a figure from a research paper. "
        "Please explain this image clearly and concisely:\n"
        "1. What type of figure is this? (chart, diagram, graph, table, photo, etc.)\n"
        "2. What is the main subject or finding shown?\n"
        "3. What are the key details, labels, or trends visible?\n"
        "4. What conclusion or insight does this figure convey?\n"
        "Keep the explanation informative but under 150 words."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    # The image as base64
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": b64_data
                        }
                    },
                    # The text prompt
                    {
                        "text": prompt_text
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        }
    }

    for api_key in api_list:
        for model_name in models:
            try:
                url  = _BASE_URL.format(model=model_name, key=api_key)
                resp = requests.post(url, json=payload, timeout=60)
                if resp.status_code == 200:
                    return (
                        resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    )
            except Exception:
                continue

    return "Explanation unavailable."


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
    Strips b64_data before saving — the PNG files are already on disk.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{paper_id}_images.json"

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
        pass


# ── Public entry point ────────────────────────────────────────────────────────

def get_or_create_images(pdf_path, paper_id=None):
    """
    Full image pipeline for one paper. Call this from anywhere.

    Returns images: [{page, index, filename, image_path, width, height, explanation}]

    Cache hit  → instant return, no extraction, no API calls.
    Cache miss → extracts images, calls Gemini Vision for each one,
                 saves PNGs to extracted_images/, saves cache JSON.

    paper_id: short stable string used as the cache key.
              Falls back to the PDF filename stem if not provided.
    """
    if not paper_id:
        paper_id = Path(pdf_path).stem[:40].replace(" ", "_").lower()

    # Fast path: return from cache
    cached = _load_cache(paper_id)
    if cached is not None:
        return cached

    # Extract all images (saves PNGs, computes b64_data in memory)
    images = extract_images_from_pdf(pdf_path)

    # Explain each image using the b64_data computed during extraction
    for i, img in enumerate(images):
        img["explanation"] = explain_image(img["b64_data"], img["page"])
        # Free-tier rate limit: ~15 requests per minute
        if i < len(images) - 1:
            time.sleep(4)

    # Save to cache (b64_data stripped — PNGs are on disk)
    _save_cache(paper_id, images)

    return images

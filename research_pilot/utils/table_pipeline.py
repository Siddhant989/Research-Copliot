"""
utils/table_pipeline.py
Full pipeline for table extraction from a single paper:

  Step 1 — Regex (PyMuPDF) finds pages containing "Table 1", "Table 2" … etc.
  Step 2 — Gemini Vision renders those pages as images, extracts tables → CSV,
            converts to Markdown, then generates a plain-English explanation.
  Step 3 — Only if Step 2 finds ZERO tables → Gemini scans all OTHER pages.

Tables are stored as Markdown strings (not CSV files) so Streamlit can render
them directly with st.markdown().

API keys are rotated on quota errors via gemini_direct_call, matching the same
fallback pattern used by the LangGraph agents.

Public entry point:
    get_or_create_tables(pdf_path, available_keys, exhausted_keys=None, paper_id=None)
    → (tables, updated_available_keys, updated_exhausted_keys)

    tables: [{page, label, caption, markdown, explanation}]

Cache file:
    extracted_assets/cache/{paper_id}_tables.json

API key rules:
  Demo mode : pass [os.getenv("GEMINI_API_KEY_1")]
  Live mode : pass state["available_api_keys"] + state["exhausted_api_keys"]
"""

import io
import re
import csv
import json
import time
import base64
from pathlib import Path

import fitz
from PIL import Image


# ── Config ────────────────────────────────────────────────────────────────────

CACHE_DIR  = Path("extracted_assets/cache")
RENDER_DPI = 150    # DPI for rendering PDF pages as images
CALL_DELAY = 3      # seconds between Gemini calls (free-tier rate limit)

# Stale error strings that invalidate a cache entry
_STALE_MARKERS = [
    "api error", "could not generate", "error 403", "error 400",
    "error 500", "error 503",
]


def _explanation_is_stale(text: str) -> bool:
    """Return True when an explanation looks like an old error string."""
    low = (text or "").lower()
    return any(m in low for m in _STALE_MARKERS)


# ── Step 1: Regex scan ────────────────────────────────────────────────────────

def find_table_pages_regex(pdf_path):
    """
    Scan every page for text that looks like a table caption:
    'Table 1', 'TABLE 2:', 'Table 3.' etc.

    Returns a sorted list of 1-indexed page numbers.
    """
    doc     = fitz.open(pdf_path)
    pattern = re.compile(r'\btable\s+\d+\b', re.IGNORECASE)
    pages   = set()

    for page_num in range(len(doc)):
        text = doc[page_num].get_text("text")
        if pattern.search(text):
            pages.add(page_num + 1)   # 1-based

    doc.close()
    return sorted(pages)


def _find_caption(pdf_path, page_num):
    """
    Try to pull the full table caption ('Table N: ...') from the page text.
    Falls back to 'Table on page N' if nothing is found.
    """
    try:
        doc  = fitz.open(pdf_path)
        page = doc[page_num - 1]   # 0-indexed
        text = page.get_text("text")
        doc.close()

        # Look for "Table N" followed by optional colon and descriptive text
        match = re.search(
            r'(Table\s+\d+[.:)—–-]?\s*[A-Za-z][^\n]{0,200})',
            text,
            re.IGNORECASE
        )
        if match:
            return match.group(1).strip()
    except Exception:
        pass

    return f"Table on page {page_num}"


# ── Step 2: Page rendering + Gemini Vision ────────────────────────────────────

def _render_page(pdf_path, page_index):
    """
    Render a PDF page (0-indexed) to a PIL Image at RENDER_DPI.
    Returns a PIL Image in RGB mode.
    """
    doc  = fitz.open(pdf_path)
    page = doc[page_index]
    mat  = fitz.Matrix(RENDER_DPI / 72, RENDER_DPI / 72)
    pix  = page.get_pixmap(matrix=mat, alpha=False)
    img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def _image_to_b64(pil_img):
    """Convert a PIL Image to a base64-encoded PNG string."""
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ── CSV → Markdown conversion ─────────────────────────────────────────────────

def csv_to_markdown(csv_text):
    """
    Convert a raw CSV string returned by Gemini into a Markdown table.
    Escapes pipe characters inside cells so the table renders correctly.
    Returns an empty string if the CSV is empty or invalid.
    """
    reader = csv.reader(io.StringIO(csv_text))
    rows   = [row for row in reader if any(c.strip() for c in row)]

    if not rows:
        return ""

    # Fill blank header cells with a placeholder
    header = [h.strip() if h.strip() else f"Col_{i+1}" for i, h in enumerate(rows[0])]

    lines = []
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    for row in rows[1:]:
        # Pad short rows and trim long rows to match header length
        padded = row + [""] * max(0, len(header) - len(row))
        cells  = [str(c).strip().replace("|", "\\|") for c in padded[:len(header)]]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


# ── Per-page extraction ───────────────────────────────────────────────────────

def extract_table_from_page(pdf_path, page_num, available_keys, exhausted_keys):
    """
    Render a page image, send it to Gemini Vision to get a CSV, convert to
    Markdown, then call Gemini again for a plain-English explanation.

    API keys are rotated on quota errors via gemini_direct_call.

    Returns (markdown_text, explanation, updated_available, updated_exhausted)
    or (None, None, updated_available, updated_exhausted) if no table found.
    """
    from utils.llm_manager import gemini_direct_call, AllKeysExhausted

    img = _render_page(pdf_path, page_num - 1)   # 0-indexed
    b64 = _image_to_b64(img)

    avail = list(available_keys)
    exh   = list(exhausted_keys)

    # ── Extract CSV from page image ───────────────────
    csv_parts = [
        {"inline_data": {"mime_type": "image/png", "data": b64}},
        {
            "text": (
                f"This is page {page_num} of a research paper. "
                "Find the table on this page and extract ALL its data. "
                "Return it ONLY as raw CSV (comma-separated, one row per line, "
                "first row = header). "
                "No explanation, no markdown fences, no extra text. "
                "If no table exists on this page, reply exactly: NO_TABLE"
            )
        },
    ]

    try:
        csv_response, avail, exh = gemini_direct_call(
            avail, exh, csv_parts, temperature=0.1, max_tokens=1024
        )
    except AllKeysExhausted as e:
        return None, None, e.available, e.exhausted

    time.sleep(CALL_DELAY)

    if csv_response.strip().upper() == "NO_TABLE":
        return None, None, avail, exh

    # Remove any markdown fences Gemini may have added
    csv_text = re.sub(r"^```[a-z]*\n?", "", csv_response, flags=re.IGNORECASE)
    csv_text = re.sub(r"\n?```$", "", csv_text).strip()

    if not csv_text:
        return None, None, avail, exh

    # Convert CSV → Markdown
    markdown = csv_to_markdown(csv_text)
    if not markdown:
        return None, None, avail, exh

    # ── Explain the table ─────────────────────────────
    explain_parts = [
        {
            "text": (
                "You are analyzing a table from a research paper.\n"
                "Here is the table in CSV format:\n\n"
                f"{csv_text}\n\n"
                "Explain this table concisely for a beginner:\n"
                "1. What is the table about?\n"
                "2. What do the rows and columns represent?\n"
                "3. Key values, trends, or comparisons?\n"
                "4. Main takeaway?\n"
                "Keep it under 150 words."
            )
        }
    ]

    try:
        explanation, avail, exh = gemini_direct_call(
            avail, exh, explain_parts, temperature=0.1, max_tokens=1024
        )
    except AllKeysExhausted as e:
        explanation = "No explanation generated."
        avail, exh  = e.available, e.exhausted

    time.sleep(CALL_DELAY)

    return markdown, explanation, avail, exh


# ── Process a list of pages ───────────────────────────────────────────────────

def _process_pages(pdf_path, pages, label, available_keys, exhausted_keys):
    """
    Run Gemini extraction on each page in the list.
    Returns (results, updated_available_keys, updated_exhausted_keys).
    """
    results = []
    avail   = list(available_keys)
    exh     = list(exhausted_keys)

    for page_num in pages:
        markdown, explanation, avail, exh = extract_table_from_page(
            pdf_path, page_num, avail, exh
        )

        if markdown is None:
            continue

        caption = _find_caption(pdf_path, page_num)
        results.append({
            "page":        page_num,
            "label":       label,
            "caption":     caption,
            "markdown":    markdown,
            "explanation": explanation,
        })

    return results, avail, exh


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _load_cache(paper_id):
    """
    Load cached table results for a paper.
    Returns a list of table dicts or None if not cached.
    Automatically invalidates caches that contain stale error explanations.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{paper_id}_tables.json"
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


def _save_cache(paper_id, tables):
    """Save table results to cache JSON. Non-fatal on failure."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{paper_id}_tables.json"
        with open(cache_file, "w") as f:
            json.dump(tables, f, indent=2, default=str)
    except Exception:
        pass


# ── Public entry point ────────────────────────────────────────────────────────

def get_or_create_tables(pdf_path, available_keys, exhausted_keys=None, paper_id=None):
    """
    Full table pipeline for one paper. Call this from anywhere.

    available_keys / exhausted_keys follow the same convention as
    invoke_with_fallback: keys are rotated on quota errors and moved to
    exhausted_keys.

    Returns (tables, updated_available_keys, updated_exhausted_keys).

    Cache hit  → instant return, zero API calls.
    Cache miss → Step 1 regex scan, Step 2 Gemini Vision on regex pages,
                 Step 3 (fallback) if Step 2 found nothing, then cache saved.

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

    doc         = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    # ── Step 1: Regex — find pages with "Table N" captions ───────────────────
    regex_pages = find_table_pages_regex(pdf_path)

    avail  = list(available_keys)
    exh    = list(exhausted_keys)
    tables = []

    if regex_pages:
        # ── Step 2: Gemini Vision on regex pages ─────────────────────────────
        tables, avail, exh = _process_pages(pdf_path, regex_pages, "regex", avail, exh)

        # ── Step 3: Fallback — only if Step 2 found nothing ──────────────────
        if not tables:
            other_pages = [p for p in range(1, total_pages + 1) if p not in regex_pages]
            tables, avail, exh = _process_pages(pdf_path, other_pages, "fallback", avail, exh)
    else:
        # Regex found nothing → scan all pages
        all_pages = list(range(1, total_pages + 1))
        tables, avail, exh = _process_pages(pdf_path, all_pages, "fallback", avail, exh)

    # Save to cache so next call is instant
    _save_cache(paper_id, tables)

    return tables, avail, exh

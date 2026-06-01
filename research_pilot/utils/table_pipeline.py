import io
import os
import re
import json
import time
import base64
import requests
from pathlib import Path

import fitz
from PIL import Image
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate


load_dotenv(override=True)


# ── Config ────────────────────────────────────────────────────────────────────

CACHE_DIR  = Path("extracted_assets/cache")
RENDER_DPI = 150    # DPI for rendering PDF pages as images
CALL_DELAY = 3      # seconds between Gemini calls (free-tier rate limit)

_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:generateContent?key={key}"
)

# Stale error strings that invalidate a cache entry
_STALE_MARKERS = [
    "api error", "could not generate", "error 403", "error 400",
    "error 500", "error 503",
]


def _explanation_is_stale(text: str) -> bool:
    """Return True when an explanation looks like an old error string."""
    low = (text or "").lower()
    return any(m in low for m in _STALE_MARKERS)


# ── Gemini Vision helper (extraction only) ────────────────────────────────────

def _gemini_call(parts, temperature=0.1):
    """
    Direct Gemini REST call for Vision-based extraction.
    Tries every GOOGLE_API_KEY_* key × [gemini-2.5-flash, gemini-2.5-pro].
    Returns the response text on success, or None if all attempts fail.
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

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": temperature},
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

    return None


# ── LangChain explanation chain ───────────────────────────────────────────────

_EXPLAIN_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You explain research-paper tables in one clear, beginner-friendly paragraph. "
     "Describe what each column means, what the numbers show, and what conclusion to draw. "
     "No bullet points. No jargon. No markdown. Plain prose only."),
    ("human",
     "Table data (JSON):\n{table_json}\n\n"
     "Write a single paragraph explaining what this table shows and what the numbers mean."),
])


def _explain_table(table_data: list) -> str:
    """
    Generate a plain-English explanation of the table using LangChain
    + invoke_with_fallback (same key-rotation pattern as all other agents).

    API keys are built from GOOGLE_API_KEY_* env vars at call time.
    Falls back to "No explanation generated." if all keys fail.
    """
    from utils.llm_manager import invoke_with_fallback

    state = {
        "available_api_keys": [
            v for k, v in os.environ.items()
            if k.startswith("GOOGLE_API_KEY_")
        ],
        "exhausted_api_keys": [],
    }

    table_json = json.dumps(table_data[:10], default=str)   # cap rows sent to LLM

    try:
        text, _ = invoke_with_fallback(state, _EXPLAIN_PROMPT, {"table_json": table_json})
        return text
    except Exception:
        return "No explanation generated."


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
    """Render a PDF page (0-indexed) to a PIL Image at RENDER_DPI."""
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


# ── Per-page extraction ───────────────────────────────────────────────────────

def extract_table_from_page(pdf_path, page_num):
    img = _render_page(pdf_path, page_num - 1)   # 0-indexed
    b64 = _image_to_b64(img)

    # ── Extract table as JSON ─────────────────────────
    parts = [
        {"inline_data": {"mime_type": "image/png", "data": b64}},
        {
            "text": f"""Extract the table from this research paper page.

Return ONLY valid JSON as a list of row objects:

[
{{"Column1":"Value1","Column2":"Value2"}},
{{"Column1":"Value3","Column2":"Value4"}}
]

Rules:
- Use table headers as keys.
- Preserve all values exactly.
- Use "" for empty cells.
- No markdown, no explanations, no code fences.
- If no table exists on this page, return [].
"""
        },
    ]

    raw = _gemini_call(parts, temperature=0.0)
    time.sleep(CALL_DELAY)

    if not raw:
        return None, None

    # Strip any markdown code fences Gemini may have added
    clean = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
    clean = re.sub(r"\n?```$", "", clean).strip()

    try:
        table_data = json.loads(clean)
    except Exception:
        return None, None

    if not table_data or not isinstance(table_data, list):
        return None, None

    # ── Explain via LangChain chain ───────────────────
    explanation = _explain_table(table_data)

    return table_data, explanation


# ── Process a list of pages ───────────────────────────────────────────────────

def _process_pages(pdf_path, pages, label):
    results = []

    for page_num in pages:
        table_data, explanation = extract_table_from_page(pdf_path, page_num)

        if table_data is None:
            continue

        caption = _find_caption(pdf_path, page_num)
        results.append({
            "page":        page_num,
            "label":       label,
            "caption":     caption,
            "table_data":  table_data,    # list of row-dicts
            "explanation": explanation,
        })

    return results


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _load_cache(paper_id):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{paper_id}_tables.json"
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


def _save_cache(paper_id, tables):
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{paper_id}_tables.json"
        with open(cache_file, "w") as f:
            json.dump(tables, f, indent=2, default=str)
    except Exception:
        pass


# ── Public entry point ────────────────────────────────────────────────────────

def get_or_create_tables(pdf_path, paper_id=None):

    if not paper_id:
        paper_id = Path(pdf_path).stem[:40].replace(" ", "_").lower()

    # Fast path: return from cache
    cached = _load_cache(paper_id)
    if cached is not None:
        return cached

    doc         = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    # ── Step 1: Regex — find pages with "Table N" captions ───────────────────
    regex_pages = find_table_pages_regex(pdf_path)
    tables      = []

    if regex_pages:
        # ── Step 2: Gemini Vision on regex pages ─────────────────────────────
        tables = _process_pages(pdf_path, regex_pages, "regex")

        # ── Step 3: Fallback — only if Step 2 found nothing ──────────────────
        if not tables:
            other_pages = [p for p in range(1, total_pages + 1) if p not in regex_pages]
            tables = _process_pages(pdf_path, other_pages, "fallback")
    else:
        # Regex found nothing → scan all pages
        tables = _process_pages(pdf_path, list(range(1, total_pages + 1)), "fallback")

    # Save to cache so next call is instant
    _save_cache(paper_id, tables)

    return tables

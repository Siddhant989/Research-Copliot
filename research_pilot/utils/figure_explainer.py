"""
utils/figure_explainer.py
Combines image and table pipelines into a single assets dict used by the
Streamlit UI and the RAG (ChromaDB) index.

For images : delegates to utils/image_pipeline.get_or_create_images()
             b64 is computed IN MEMORY during extraction — no file re-read.
             Cache: extracted_assets/cache/{paper_id}_images.json

For tables : delegates to utils/table_pipeline.get_or_create_tables()
             Renders pages as images, Gemini Vision extracts → CSV → Markdown.
             Regex first (Step 1), Gemini on regex pages (Step 2),
             fallback to all other pages only if Step 2 finds nothing (Step 3).
             Cache: extracted_assets/cache/{paper_id}_tables.json

API keys are rotated on quota errors through both pipelines via
gemini_direct_call, matching the same fallback pattern as the LangGraph agents.

Public entry point:
    get_or_create_assets(pdf_path, available_keys, exhausted_keys=None, paper_id=None)
    → (assets, updated_available_keys, updated_exhausted_keys)

    assets: {"figures": [...], "tables": [...]}

    figures: {page, index, filename, image_path, width, height, explanation}
    tables:  {page, label, caption, markdown, explanation}

Also exported for app.py demo loader:
    _load_cache(paper_id)  → assets dict or None
"""

import json
from pathlib import Path


CACHE_DIR = Path("extracted_assets/cache")

# Stale error strings written by old code that lacked proper error handling
_STALE_MARKERS = [
    "api error", "could not generate", "error 403", "error 400",
    "error 500", "error 503",
]


def _explanation_is_stale(text: str) -> bool:
    """Return True when an explanation looks like an old error string."""
    low = (text or "").lower()
    return any(m in low for m in _STALE_MARKERS)


def _assets_cache_is_stale(cached: dict) -> bool:
    """
    Return True if any figure or table in the combined cache has a stale
    error explanation that must be regenerated.
    """
    for section in ("figures", "tables"):
        for item in cached.get(section, []):
            if _explanation_is_stale(item.get("explanation", "")):
                return True
    return False


# ── Cache helpers (also used by app.py demo loader) ───────────────────────────

def _load_cache(paper_id):
    """
    Load combined assets from cache.
    Returns {"figures": [...], "tables": [...]} or None if not cached.
    Automatically invalidates caches that contain stale error explanations.
    """
    cache_file = CACHE_DIR / f"{paper_id}_assets.json"
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r") as f:
            cached = json.load(f)
        if isinstance(cached, dict) and "figures" in cached:
            if _assets_cache_is_stale(cached):
                # Remove the stale combined cache so it gets regenerated
                cache_file.unlink(missing_ok=True)
                return None
            return cached
    except Exception:
        pass
    return None


def _save_cache(paper_id, assets):
    """Save combined assets dict to cache JSON. Non-fatal on failure."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{paper_id}_assets.json"
        with open(cache_file, "w") as f:
            json.dump(assets, f, default=str, indent=2)
    except Exception:
        pass


# ── Public entry point ────────────────────────────────────────────────────────

def get_or_create_assets(pdf_path, available_keys, exhausted_keys=None, paper_id=None):
    """
    Returns (assets, updated_available_keys, updated_exhausted_keys).

    assets: {"figures": [...], "tables": [...]}

    Both pipelines are cache-aware and share the same key-rotation fallback.
    On a combined cache hit the full dict is returned instantly with zero
    extraction and zero API calls.

    available_keys / exhausted_keys follow the same convention as
    invoke_with_fallback: keys are rotated on quota errors and moved to
    exhausted_keys.

    paper_id: short stable string used as the cache key.
              Falls back to the PDF filename stem if not provided.
    """
    if exhausted_keys is None:
        exhausted_keys = []

    if not paper_id:
        paper_id = Path(pdf_path).stem[:40].replace(" ", "_").lower()

    # Return from combined cache if available
    cached = _load_cache(paper_id)
    if cached is not None:
        return cached, list(available_keys), list(exhausted_keys)

    avail = list(available_keys)
    exh   = list(exhausted_keys)

    # ── Images: b64 computed in memory during extraction, sent directly to Gemini
    from utils.image_pipeline import get_or_create_images
    figures, avail, exh = get_or_create_images(pdf_path, avail, exh, paper_id=paper_id)

    # ── Tables: regex scan → Gemini Vision → CSV → Markdown → explanation
    from utils.table_pipeline import get_or_create_tables
    tables, avail, exh = get_or_create_tables(pdf_path, avail, exh, paper_id=paper_id)

    assets = {"figures": figures, "tables": tables}

    # Save combined cache so next call is instant
    _save_cache(paper_id, assets)

    return assets, avail, exh

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

def get_or_create_assets(pdf_path, paper_id=None):
    """
    Returns assets: {"figures": [...], "tables": [...]}

    Both pipelines are cache-aware. API keys are read from GOOGLE_API_KEY_*
    environment variables directly inside each pipeline — no key params needed.

    On a combined cache hit the full dict is returned instantly with zero
    extraction and zero API calls.

    paper_id: short stable string used as the cache key.
              Falls back to the PDF filename stem if not provided.
    """
    if not paper_id:
        paper_id = Path(pdf_path).stem[:40].replace(" ", "_").lower()

    # Return from combined cache if available
    cached = _load_cache(paper_id)
    if cached is not None:
        return cached

    # ── Images: b64 computed in memory during extraction, sent directly to Gemini
    from utils.image_pipeline import get_or_create_images
    figures = get_or_create_images(pdf_path, paper_id=paper_id)

    # ── Tables: regex scan → Gemini Vision → CSV → Markdown → explanation
    from utils.table_pipeline import get_or_create_tables
    tables = get_or_create_tables(pdf_path, paper_id=paper_id)

    assets = {"figures": figures, "tables": tables}

    # Save combined cache so next call is instant
    _save_cache(paper_id, assets)

    return assets

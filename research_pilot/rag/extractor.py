"""
rag/extractor.py — PyMuPDF figure + table extraction.
Every figure is saved as a PNG in extracted_assets/figures/.
Every table is returned as a list-of-lists (header row first).
"""

import hashlib
from pathlib import Path

import fitz  # PyMuPDF

FIGURES_DIR = Path("extracted_assets/figures")

# Skip images smaller than this (icons, bullets, logos)
MIN_W = 100
MIN_H = 100


# ── Caption helpers ───────────────────────────────────────────────────────────

def _text_near(page: fitz.Page, bbox, search_pts: int = 70) -> str:
    """Return the text in a strip above/below the given bounding box."""
    x0, y0, x1, y1 = bbox
    ph = page.rect.height

    below = fitz.Rect(0, y1, page.rect.width, min(ph, y1 + search_pts))
    above = fitz.Rect(0, max(0, y0 - search_pts), page.rect.width, y0)

    for rect in (below, above):
        txt = page.get_text("text", clip=rect).strip()
        if txt:
            return txt
    return ""


def _find_caption(page: fitz.Page, bbox, prefix: str) -> str:
    """Look for a line starting with prefix (e.g. 'Figure', 'Table') near bbox."""
    raw = _text_near(page, bbox, search_pts=90)
    for line in raw.split("\n"):
        line = line.strip()
        if line.lower().startswith(prefix.lower()):
            return line[:240]
    return ""


def _page_section(page: fitz.Page) -> str:
    """Heuristic: return the first large/bold span text on the page as a section name."""
    try:
        for block in page.get_text("dict").get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    txt  = span.get("text", "").strip()
                    size = span.get("size", 0)
                    if 10 < size < 70 and 3 < len(txt) < 60:
                        return txt.lower()
    except Exception:
        pass
    return ""


# ── Figure extraction ─────────────────────────────────────────────────────────

def extract_figures(pdf_path: str) -> list:
    """
    Extract all meaningful images from the PDF.
    Returns a list of figure dicts, one per unique image.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    doc      = fitz.open(pdf_path)
    figures  = []
    seen_md5 = set()

    for page_no, page in enumerate(doc, start=1):
        section   = _page_section(page)
        img_infos = page.get_image_info(xrefs=True)  # [{xref, bbox, ...}, ...]

        for info in img_infos:
            xref = info.get("xref", 0)
            if xref == 0:
                continue
            bbox = info.get("bbox", (0, 0, 0, 0))
            w    = bbox[2] - bbox[0]
            h    = bbox[3] - bbox[1]
            if w < MIN_W or h < MIN_H:
                continue

            try:
                img_dict = doc.extract_image(xref)
            except Exception:
                continue
            if not img_dict:
                continue

            raw_bytes = img_dict["image"]
            md5       = hashlib.md5(raw_bytes).hexdigest()
            if md5 in seen_md5:
                continue
            seen_md5.add(md5)

            ext      = img_dict.get("ext", "png")
            filename = f"p{page_no}_{md5[:10]}.{ext}"
            img_path = FIGURES_DIR / filename
            img_path.write_bytes(raw_bytes)

            caption = _find_caption(page, bbox, "Figure") or f"Figure on page {page_no}"
            figures.append({
                "type":         "figure",
                "page_number":  page_no,
                "section_name": section,
                "caption":      caption,
                "image_path":   str(img_path),
                "width":        int(img_dict.get("width",  w)),
                "height":       int(img_dict.get("height", h)),
                "explanation":  "",   # filled by explainer later
            })

    doc.close()
    return figures


# ── Table extraction ──────────────────────────────────────────────────────────

def _clean_row(row: list) -> list:
    """Replace None cells with empty string, strip whitespace."""
    return [str(cell).strip() if cell is not None else "" for cell in row]


def extract_tables(pdf_path: str) -> list:
    """
    Extract all tables from the PDF via PyMuPDF's find_tables().
    Requires PyMuPDF >= 1.23.0.
    Returns a list of table dicts.
    """
    doc    = fitz.open(pdf_path)
    tables = []

    for page_no, page in enumerate(doc, start=1):
        section = _page_section(page)

        try:
            finder   = page.find_tables()
            tab_list = list(finder)          # TableFinder is iterable
        except (AttributeError, Exception):
            continue                          # old PyMuPDF or no tables

        for tab in tab_list:
            try:
                raw = tab.extract()
            except Exception:
                continue

            if not raw or len(raw) < 2:      # skip single-row or empty
                continue

            # Clean cells
            cleaned = [_clean_row(row) for row in raw]

            # Caption
            try:
                caption = _find_caption(page, tab.bbox, "Table") or f"Table on page {page_no}"
            except Exception:
                caption = f"Table on page {page_no}"

            tables.append({
                "type":         "table",
                "page_number":  page_no,
                "section_name": section,
                "caption":      caption,
                "table_data":   cleaned,
                "explanation":  "",   # filled by explainer later
            })

    doc.close()
    return tables


# ── Public entry point ────────────────────────────────────────────────────────

def extract_all(pdf_path: str) -> dict:
    """Run both extractions. Returns {"figures": [...], "tables": [...]}."""
    return {
        "figures": extract_figures(pdf_path),
        "tables":  extract_tables(pdf_path),
    }

"""
utils/pdf_parser.py
Full PDF parsing with PyMuPDF: extracts raw text (with page markers),
abstract, and section dictionary.
"""

import re
import base64
import fitz   # PyMuPDF




def _clean(text):

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()


def _extract_abstract(text):

    lower_text = text.lower()

    start = lower_text.find("abstract")

    if start != -1:

        abstract_text = text[start + len("abstract"):]

        end = abstract_text.lower().find("introduction")

        if end != -1:
            return abstract_text[:end].strip()[:800]

        return abstract_text[:800]

    lines = text.split("\n")

    long_lines = []

    for line in lines:

        if len(line.strip()) > 60:
            long_lines.append(line.strip())

        if len(long_lines) >= 4:
            break

    return " ".join(long_lines)[:800]


_SECTION_RE = re.compile(
    r"^(?:\d+\.?\s+)?([A-Z][A-Za-z &\-]{2,50})$",
    re.MULTILINE
)

_COMMON_HEADERS = {
    "abstract",
    "introduction",
    "related work",
    "background",
    "methodology",
    "method",
    "approach",
    "model",
    "architecture",
    "experiments",
    "results",
    "evaluation",
    "discussion",
    "conclusion",
    "references",
    "acknowledgements",
    "appendix"
}


def _extract_sections(raw):

    sections = {}

    current_name = "preamble"

    current_lines = []

    lines = raw.split("\n")

    for line in lines:

        stripped = line.strip()

        is_header = False

        if stripped and len(stripped) < 60:

            if stripped.lower() in _COMMON_HEADERS:
                is_header = True

            elif _SECTION_RE.match(stripped):
                is_header = True

        if is_header:

            if current_lines:

                sections[current_name] = "\n".join(
                    current_lines
                ).strip()

            current_name = stripped.lower()

            current_lines = []

        else:

            current_lines.append(line)

    if current_lines:

        sections[current_name] = "\n".join(
            current_lines
        ).strip()

    return sections


# ── Public API ───────────────────────────────────────────────────────────────

def extract_figures(pdf_path: str) -> list:
    """
    Extract images from a PDF as base64 data URIs.
    Skips tiny images (<120px), returns up to 6 largest unique figures.
    """
    doc = fitz.open(pdf_path)
    candidates = []
    for page_num in range(min(len(doc), 15)):
        page = doc[page_num]
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                base_img = doc.extract_image(xref)
            except Exception:
                continue
            w = base_img.get("width",  0)
            h = base_img.get("height", 0)
            if w < 120 or h < 120:
                continue
            ext  = base_img.get("ext", "png")
            b64  = base64.b64encode(base_img["image"]).decode()
            candidates.append({
                "page":    page_num + 1,
                "width":   w,
                "height":  h,
                "ext":     ext,
                "caption": f"Figure — Page {page_num + 1}",
                "data":    f"data:image/{ext};base64,{b64}",
            })
    doc.close()

    candidates.sort(key=lambda x: x["width"] * x["height"], reverse=True)
    seen, unique = set(), []
    for f in candidates:
        key = (f["page"], f["width"], f["height"])
        if key not in seen:
            seen.add(key)
            unique.append(f)
        if len(unique) >= 6:
            break
    return unique


def parse_pdf(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    page_count = len(doc)

    pages_text = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            pages_text.append(f"[Page {i}]\n{text}")

    doc.close()

    raw_text = _clean("\n".join(pages_text))
    abstract = _extract_abstract(raw_text)
    sections = _extract_sections(raw_text)

    return {
        "raw_text":   raw_text,
        "abstract":   abstract,
        "sections":   sections,
        "page_count": page_count,
    }

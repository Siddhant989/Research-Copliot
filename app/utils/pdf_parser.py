"""
app/utils/pdf_parser.py — Extract structured data from PDF research papers.

PyMuPDF (imported as `fitz`) reads the PDF binary and lets us pull out:
  • All text, page by page
  • Document metadata (title, author — when embedded by the author's tool)
  • Page count / word count

We also run lightweight regex passes to detect reproducibility signals
(GitHub links, dataset names, "code available" phrases) so the ReproScorer
has richer evidence than the abstract alone.
"""

import re
import fitz  # PyMuPDF — installed as the `pymupdf` package


# ── Patterns for reproducibility signal detection ─────────────────────────────

_CODE_PATTERNS = [
    r"github\.com/[\w\-]+/[\w\-]+",   # GitHub repo URL
    r"code\s+(?:is\s+)?available",
    r"open[- ]source",
    r"implementation\s+(?:is\s+)?(?:publicly\s+)?(?:available|released)",
    r"https?://[\w./\-]+(?:code|repo|implementation)",
]

_DATASET_PATTERNS = [
    r"\bImageNet\b", r"\bCIFAR[-\s]\d+\b", r"\bMNIST\b",
    r"\bCOCO\b",     r"\bSQuAD\b",          r"\bGLUE\b",
    r"\bSuperGLUE\b",r"\bOpenWebText\b",     r"\bC4\b",
    r"\bCommonCrawl\b", r"\bWikiText\b",     r"\bPTB\b",
    r"\bMS[- ]?MARCO\b", r"\bNaturalQuestions\b",
    r"dataset\s+(?:is\s+)?(?:publicly\s+)?available",
    r"data\s+(?:is\s+)?(?:publicly\s+)?available",
]


def _find_code_mentions(text: str) -> list[str]:
    """Return all unique code/repo signals found in the text."""
    found = set()
    for pattern in _CODE_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            found.add(match.strip())
    return list(found)


def _find_dataset_mentions(text: str) -> list[str]:
    """Return all unique dataset names / availability signals found."""
    found = set()
    for pattern in _DATASET_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            found.add(match.strip())
    return list(found)


def _extract_abstract(text: str) -> str:
    """
    Attempt to pull the abstract section from raw paper text.
    Strategy: find the word 'abstract', then take the next ~600 chars
    up to the first section-heading keyword.
    """
    # Case-insensitive search for "abstract" as a standalone word / heading
    match = re.search(r"\babstract\b", text, re.IGNORECASE)
    if not match:
        # No abstract heading — use the first 600 characters as a proxy
        return text[:600].strip()

    start = match.end()
    snippet = text[start:start + 1500]

    # Cut off at the next section heading (e.g. "1. Introduction", "Keywords")
    cut = re.search(
        r"\n\s*(?:\d+[\.\s]+[A-Z]|introduction|keywords|related work|background)",
        snippet,
        re.IGNORECASE,
    )
    if cut:
        snippet = snippet[: cut.start()]

    return snippet.strip()[:800]  # cap at ~800 chars


def _guess_title(first_page_text: str) -> str:
    """
    Heuristic: the title is usually the first long, non-metadata line
    on page 1 (before the author list).
    """
    for line in first_page_text.splitlines():
        line = line.strip()
        # Skip short lines, arXiv IDs, URLs, and lines that look like metadata
        if len(line) >= 20 and not re.match(r"(https?|arXiv|doi|\d{4}\.\d+)", line):
            return line
    return ""


# ── Public API ────────────────────────────────────────────────────────────────

def parse_pdf(filepath: str) -> dict:
    """
    Open a PDF file and return a structured dict compatible with the
    ResearchState `papers` list format used by arXiv results.

    Extra keys added for PDF mode:
      full_text        — complete extracted text (for deep repro scoring)
      page_count       — number of pages
      word_count       — approximate word count
      code_mentions    — list of detected code/repo signals
      dataset_mentions — list of detected dataset signals
      source           — always "pdf_upload" so agents know the data origin
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        raise ValueError(f"Cannot open PDF: {e}")

    # ── Extract text ──────────────────────────────────────────────────────
    pages_text = [page.get_text() for page in doc]
    full_text = "\n".join(pages_text)

    # ── Metadata ──────────────────────────────────────────────────────────
    meta = doc.metadata or {}
    title   = meta.get("title", "").strip()
    authors = meta.get("author", "").strip()

    # Fall back to heuristics when metadata is empty (common for arXiv PDFs)
    if not title and pages_text:
        title = _guess_title(pages_text[0])
    if not title:
        title = "Uploaded Paper"
    if not authors:
        authors = "Unknown Authors"

    abstract = _extract_abstract(full_text)

    return {
        # Fields shared with arXiv paper dicts
        "title":      title,
        "authors":    [a.strip() for a in authors.split(";") if a.strip()] or [authors],
        "abstract":   abstract,
        "url":        "",           # no URL for local PDFs
        "published":  "",
        "categories": [],

        # PDF-only fields
        "full_text":        full_text,
        "page_count":       len(doc),
        "word_count":       len(full_text.split()),
        "code_mentions":    _find_code_mentions(full_text),
        "dataset_mentions": _find_dataset_mentions(full_text),
        "source":           "pdf_upload",
    }

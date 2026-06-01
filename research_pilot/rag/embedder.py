"""
rag/embedder.py — ChromaDB + HuggingFace sentence-transformer embeddings.

Singleton pattern: one client + one collection reused for the lifetime of the
Streamlit process. Call reset_and_build(assets) to wipe & re-index a new paper.
"""

import json

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_PATH     = ".chroma_db"
COLLECTION_NAME = "rp_rag_v1"
HF_MODEL        = "all-MiniLM-L6-v2"

# ── Module-level singletons ───────────────────────────────────────────────────
_client = None   # ChromaDB client instance (created once, reused)
_col    = None   # ChromaDB collection instance


def _embedding_function() -> SentenceTransformerEmbeddingFunction:
    return SentenceTransformerEmbeddingFunction(model_name=HF_MODEL)


def get_collection():
    """Return the shared collection, initialising ChromaDB if needed."""
    global _client, _col
    if _col is not None:
        return _col
    _client = chromadb.PersistentClient(path=CHROMA_PATH)
    _col = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )
    return _col


def _drop_collection() -> None:
    """Delete the existing collection so we can start fresh for a new paper."""
    global _client, _col
    c = get_collection()   # ensure _client is set
    try:
        _client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    _col = None


def reset_and_build(assets: dict) -> chromadb.Collection:
    """
    Wipe the existing index and re-index figures + tables from `assets`.

    Figures come from image_pipeline:
        {page, index, filename, image_path, width, height, explanation}

    Tables come from table_pipeline:
        {page, label, caption, markdown, explanation}

    The explanation text is used as the primary searchable document so that
    Q&A retrieval finds semantically relevant content, not just caption matches.
    """
    _drop_collection()
    col = get_collection()

    docs  = []
    metas = []
    ids   = []

    # ── Figures ───────────────────────────────────────────────────────────────
    for i, fig in enumerate(assets.get("figures", [])):
        # page_number field (image_pipeline uses "page", rag/extractor uses "page_number")
        page_num = str(fig.get("page_number") or fig.get("page", ""))
        caption  = fig.get("caption") or f"Figure on page {page_num}"
        section  = str(fig.get("section_name") or "")
        expl     = fig.get("explanation") or caption

        # Use explanation as the searchable document — richer than just caption
        docs.append(expl[:1000])
        metas.append({
            "type":         "figure",
            "page_number":  page_num,
            "section_name": section,
            "caption":      caption[:500],
            "image_path":   str(fig.get("image_path") or ""),
            "markdown":     "",   # not applicable for figures
        })
        ids.append(f"fig_{i}")

    # ── Tables ────────────────────────────────────────────────────────────────
    for i, tbl in enumerate(assets.get("tables", [])):
        # page field (table_pipeline uses "page", rag/extractor uses "page_number")
        page_num   = str(tbl.get("page_number") or tbl.get("page", ""))
        caption    = tbl.get("caption") or f"Table on page {page_num}"
        section    = str(tbl.get("section_name") or tbl.get("label") or "")
        expl       = tbl.get("explanation") or caption
        # table_data is a list-of-dicts; serialise to JSON string for metadata storage
        table_data = tbl.get("table_data") or []
        table_json = json.dumps(table_data, default=str)[:4000]

        # Embed caption + explanation for richer retrieval
        embed_text = f"{caption} {expl}".strip()[:1000]

        docs.append(embed_text)
        metas.append({
            "type":         "table",
            "page_number":  page_num,
            "section_name": section,
            "caption":      caption[:500],
            "image_path":   "",          # not applicable for tables
            "table_data":   table_json,  # JSON string; parse with json.loads() in UI
        })
        ids.append(f"tbl_{i}")

    if docs:
        col.add(documents=docs, metadatas=metas, ids=ids)

    return col

"""
rag/retriever.py — Multi-query retrieval with deduplication and re-ranking.

Pipeline:
  1. Generate 3 alternative phrasings of the user question via Gemini.
  2. Query ChromaDB with each phrasing.
  3. Merge all results, deduplicate by caption, re-rank by similarity score.
  4. Return the top-k most relevant chunks.
"""

import json
import re

from langchain_core.prompts import ChatPromptTemplate

from agents.llm  import llm
from rag.embedder import get_collection

# ── Multi-query prompt ────────────────────────────────────────────────────────

_MQ_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You help improve document retrieval by generating alternative phrasings of a question. "
     "Return ONLY a JSON array of exactly 3 strings. No explanation, no markdown."),
    ("human",
     "Original question: {question}\n\nGenerate 3 alternative phrasings."),
])


def _generate_variants(question):
    """Ask Gemini for 3 alternative phrasings; fall back to simple templates on error."""
    try:
        chain = _MQ_PROMPT | llm
        resp  = chain.invoke({"question": question})
        text  = re.sub(r"```(?:json)?", "", resp.content).strip().rstrip("`").strip()
        variants = json.loads(text)
        if isinstance(variants, list) and variants:
            return [str(v) for v in variants[:3]]
    except Exception:
        pass

    # Deterministic fallback — no LLM required
    q = question.lower().strip("? \t\n")
    return [
        question,
        f"What does the paper say about {q}?",
        f"Describe {q} as presented in this research paper.",
    ]


# ── Core retrieval ────────────────────────────────────────────────────────────

def retrieve(question, top_k=5):
    """
    Multi-query RAG retrieval.

    Returns a list of up to `top_k` dicts:
      {
        "document": str,          # the embedded text (caption / header)
        "metadata": dict,         # {type, page_number, section_name, caption,
                                  #  image_path, table_data (JSON str)}
        "score":    float,        # cosine similarity 0-1
      }
    Results are deduplicated by caption and sorted by score descending.
    """
    col = get_collection()
    if col.count() == 0:
        return []

    n_results = min(top_k, col.count())

    # Build query list: original question + 3 LLM-generated variants, no duplicates
    variants = _generate_variants(question)
    all_queries_raw = [question] + variants
    all_queries = []
    for q in all_queries_raw:
        if q not in all_queries:
            all_queries.append(q)
    all_queries = all_queries[:4]

    seen = set()
    candidates = []

    for q_text in all_queries:
        try:
            result = col.query(
                query_texts=[q_text],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            continue

        docs      = result.get("documents",  [[]])[0]
        metas     = result.get("metadatas",  [[]])[0]
        distances = result.get("distances",   [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            # Deduplication key: caption (capped) for stability
            dedup_key = meta.get("caption", doc)[:80]
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            # Convert cosine distance → similarity (ChromaDB returns 0=identical)
            score = max(0.0, 1.0 - float(dist))

            candidates.append({
                "document": doc,
                "metadata": meta,
                "score":    score,
            })

    # Re-rank by similarity score descending
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[:top_k]

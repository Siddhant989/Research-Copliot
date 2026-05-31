"""
rag/explainer.py — Gemini explanations for figures, tables, and Q&A answers.
Uses the shared agents/llm.py LangChain LLM instance.
"""

import json

from langchain_core.prompts import ChatPromptTemplate

from agents.llm import llm


# ── Figure explanation ────────────────────────────────────────────────────────

_FIG_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You explain research-paper figures in one clear, beginner-friendly paragraph. "
     "No bullet points. No jargon. No markdown. Imagine you are explaining it to a smart friend "
     "who has not read the paper. Write plain prose only."),
    ("human",
     "Paper title: {title}\n"
     "Figure caption: {caption}\n"
     "Page number: {page}\n"
     "Section: {section}\n\n"
     "Write a single paragraph explaining what this figure shows and why it matters."),
])


def explain_figure(
    caption: str,
    title:   str = "",
    page:    int = 0,
    section: str = "",
) -> str:
    """Return a one-paragraph plain-English explanation of a figure."""
    try:
        chain = _FIG_PROMPT | llm
        resp  = chain.invoke({
            "title":   title,
            "caption": caption,
            "page":    page,
            "section": section,
        })
        return resp.content.strip()
    except Exception:
        return (
            f"This figure (page {page}) is titled: \"{caption}\". "
            "It is part of the paper's visual explanation of the methodology or results."
        )


# ── Table explanation ─────────────────────────────────────────────────────────

_TBL_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You explain research-paper tables in one clear, beginner-friendly paragraph. "
     "Describe what each column means, what the numbers show, and what conclusion to draw. "
     "No bullet points. No jargon. No markdown. Plain prose only."),
    ("human",
     "Paper title: {title}\n"
     "Table caption: {caption}\n"
     "Page number: {page}\n"
     "Section: {section}\n"
     "First few rows of data: {data}\n\n"
     "Write a single paragraph explaining what this table shows and what the numbers mean."),
])


def explain_table(
    caption:    str,
    table_data: list,
    title:      str = "",
    page:       int = 0,
    section:    str = "",
) -> str:
    """Return a one-paragraph plain-English explanation of a table."""
    try:
        sample   = table_data[:6]
        data_str = json.dumps(sample, default=str)[:1000]
        chain    = _TBL_PROMPT | llm
        resp     = chain.invoke({
            "title":   title,
            "caption": caption,
            "page":    page,
            "section": section,
            "data":    data_str,
        })
        return resp.content.strip()
    except Exception:
        return (
            f"This table (page {page}) is titled: \"{caption}\". "
            "It compares values across the rows and columns described in the caption."
        )


# ── Q&A answer ────────────────────────────────────────────────────────────────

_QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a research assistant helping a beginner understand a research paper. "
     "Answer the question using ONLY the context provided below. "
     "Be clear, plain, and friendly — avoid jargon. "
     "If the context does not cover the question, say so honestly. "
     "Do not make up information."),
    ("human",
     "Paper: {title}\n\n"
     "--- Context retrieved from the paper ---\n"
     "{context}\n"
     "--- End of context ---\n\n"
     "Question: {question}"),
])


def answer_question(
    question: str,
    chunks:   list,
    title:    str  = "",
    state:    dict = None,
) -> tuple:
    """
    Generate a beginner-friendly answer using retrieved chunks as context.

    When `state` contains `available_api_keys` (live pipeline mode), uses
    invoke_with_fallback so API keys are rotated on quota errors exactly like
    the LangGraph agents. Falls back to the singleton LLM otherwise (demo mode).

    chunks: list of dicts from retriever.retrieve()
      Each chunk has "document", "metadata", "score".

    Returns (answer_text, key_updates_dict_or_None).
    key_updates has "available_api_keys" and "exhausted_api_keys" when
    invoke_with_fallback was used; None when the singleton LLM was used.
    """
    if not chunks:
        return (
            "I could not find relevant passages in this paper to answer your question. "
            "Try rephrasing or asking about a different topic covered in the paper.",
            None,
        )

    # Build context string from top chunks
    context_parts = []
    for c in chunks:
        meta    = c.get("metadata", {})
        ctype   = meta.get("type", "passage").upper()
        page    = meta.get("page_number", "?")
        section = meta.get("section_name", "")
        text    = c.get("document", "")
        context_parts.append(
            f"[{ctype} · Page {page} · {section}]\n{text}"
        )
    context = "\n\n---\n\n".join(context_parts)[:3500]

    variables = {
        "title":    title,
        "context":  context,
        "question": question,
    }

    # ── Live mode: key-rotation fallback ──────────────────────────────────────
    if state is not None and state.get("available_api_keys"):
        from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
        try:
            text, key_updates = invoke_with_fallback(state, _QA_PROMPT, variables)
            return text.strip(), key_updates
        except AllKeysExhausted as e:
            return (
                "All API keys have been exhausted. Could not generate an answer. "
                "Please provide a fresh key to continue.",
                {"available_api_keys": e.available, "exhausted_api_keys": e.exhausted},
            )
        except Exception as e:
            return f"Could not generate an answer: {str(e)[:120]}", None

    # ── Demo / no-state mode: singleton LLM ───────────────────────────────────
    try:
        chain = _QA_PROMPT | llm
        resp  = chain.invoke(variables)
        return resp.content.strip(), None
    except Exception as e:
        return f"Could not generate an answer: {str(e)[:120]}", None

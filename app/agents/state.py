"""
app/agents/state.py — The shared "memory" that all LangGraph agents read & write.

Think of ResearchState as a whiteboard that every agent in the pipeline can see.
Each agent reads what it needs, does its work, and writes its results back.
LangGraph passes this dict from node to node automatically.
"""

from typing import TypedDict


class ResearchState(TypedDict):
    # ── Inputs ────────────────────────────────────────────────────────────────
    query: str               # Original topic the user typed in the UI

    # ── Planner output ────────────────────────────────────────────────────────
    refined_query: str       # Planner's improved, search-friendly version of query

    # ── Research output ───────────────────────────────────────────────────────
    papers: list             # List of dicts fetched from arXiv:
                             # {title, authors, abstract, url, published, categories}

    # ── Critic output ─────────────────────────────────────────────────────────
    critique: str            # Paragraph identifying gaps / weaknesses in the papers

    # ── Hypothesis output ─────────────────────────────────────────────────────
    hypotheses: list         # List of strings, each a testable hypothesis

    # ── Memory output ─────────────────────────────────────────────────────────
    key_findings: list       # Bullet-point findings distilled from all papers

    # ── Reproducibility Scorer output ─────────────────────────────────────────
    repro_scores: list       # List of dicts: {title, score (0-10), reasoning}

    # ── Synthesizer output ────────────────────────────────────────────────────
    synthesis: str           # Final executive-summary report

    # ── Error tracking ────────────────────────────────────────────────────────
    errors: list             # Any error messages collected along the way

"""
app/agents/state.py — The shared "whiteboard" that all LangGraph agents read & write.

Every field here is visible to every agent.  Each agent reads what it needs,
does its work, and returns a PARTIAL dict with only the fields it changed.
LangGraph merges that partial dict back into the full state automatically.

Phase 5 adds three fields to support the Critic ↔ Hypothesis feedback loop:
  hypothesis_iterations — how many times Hypothesis has run (starts at 0)
  hypothesis_quality    — Evaluator's verdict: "pass" or "retry"
  evaluator_feedback    — Evaluator's written notes on what to improve
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

    # ── Hypothesis feedback loop (Phase 5) ────────────────────────────────────
    hypothesis_iterations: int  # How many times Hypothesis agent has run (0 = not yet)
    hypothesis_quality:    str  # Evaluator's verdict: "pass" | "retry"
    evaluator_feedback:    str  # What Evaluator told Hypothesis to improve

    # ── Memory output ─────────────────────────────────────────────────────────
    key_findings: list       # Bullet-point findings distilled from all papers

    # ── Reproducibility Scorer output ─────────────────────────────────────────
    repro_scores: list       # List of dicts: {title, score (0-10), reasoning}

    # ── Synthesizer output ────────────────────────────────────────────────────
    synthesis: str           # Final executive-summary report

    # ── Error tracking ────────────────────────────────────────────────────────
    errors: list             # Any error messages collected along the way

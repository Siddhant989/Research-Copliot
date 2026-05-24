"""
app/agents/state.py — The shared whiteboard every agent reads and writes.

LangGraph passes this dict from node to node automatically.
Each agent only returns the fields it changes — LangGraph merges the rest.
"""

from typing import TypedDict


class ResearchState(TypedDict):
    # ── Input ─────────────────────────────────────────────────────────────────
    query: str               # What the user typed

    # ── Planner ───────────────────────────────────────────────────────────────
    refined_query: str       # Search-optimised version of the query

    # ── Research ──────────────────────────────────────────────────────────────
    papers: list             # [{title, authors, abstract, url, published, categories}]

    # ── Critic ────────────────────────────────────────────────────────────────
    critique: str            # Plain-English gaps in the literature

    # ── Hypothesis (with feedback loop) ───────────────────────────────────────
    hypotheses:             list   # ["H: ...", ...]
    hypothesis_iterations:  int    # how many times Hypothesis has run
    hypothesis_quality:     str    # "pass" | "retry"
    evaluator_feedback:     str    # written notes from Evaluator on what to fix

    # ── Memory ────────────────────────────────────────────────────────────────
    key_findings: list       # ["• ...", ...]

    # ── Reproducibility Scorer ────────────────────────────────────────────────
    repro_scores: list       # [{title, score, reasoning, code_mentions, dataset_mentions}]

    # ── Tech Analyzer (new) ───────────────────────────────────────────────────
    model_profiles: list     # [{paper, architecture, key_components, parameters,
                             #   training_data, compute, framework}]
    code_snippet:   str      # Runnable Python snippet for the core concept

    # ── Synthesizer — structured per-paper analysis ──────────────────────────
    methodology: list   # [{paper, approach, how_tested, steps:[...]}]
    assumptions: list   # [{paper, assumptions:[...]}]
    weaknesses:  list   # [{paper, weaknesses:[...]}]

    # ── Synthesizer ───────────────────────────────────────────────────────────
    synthesis: str           # Final plain-English report (Markdown)

    # ── Errors ────────────────────────────────────────────────────────────────
    errors: list

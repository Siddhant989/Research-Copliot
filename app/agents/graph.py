"""
app/agents/graph.py — LangGraph pipelines for ResearchPilot AI.

Two pipelines are defined here:

  pipeline     (arXiv mode)  — all 7 agents
    Planner → Research → Critic → Hypothesis → Memory → ReproScorer → Synthesizer

  pdf_pipeline (PDF mode)    — 5 agents (Planner + Research are skipped because
    the paper is already provided by the user)
    Critic → Hypothesis → Memory → ReproScorer → Synthesizer
"""

from langgraph.graph import StateGraph, END

from app.agents.state import ResearchState
from app.agents.planner     import planner_node
from app.agents.research     import research_node
from app.agents.critic       import critic_node
from app.agents.hypothesis   import hypothesis_node
from app.agents.memory       import memory_node
from app.agents.repro_scorer import repro_scorer_node
from app.agents.synthesizer  import synthesizer_node


# ── Pipeline 1: arXiv research (7 agents) ─────────────────────────────────────

def _build_arxiv_graph():
    g = StateGraph(ResearchState)

    g.add_node("planner",      planner_node)
    g.add_node("research",     research_node)
    g.add_node("critic",       critic_node)
    g.add_node("hypothesis",   hypothesis_node)
    g.add_node("memory",       memory_node)
    g.add_node("repro_scorer", repro_scorer_node)
    g.add_node("synthesizer",  synthesizer_node)

    g.set_entry_point("planner")
    g.add_edge("planner",      "research")
    g.add_edge("research",     "critic")
    g.add_edge("critic",       "hypothesis")
    g.add_edge("hypothesis",   "memory")
    g.add_edge("memory",       "repro_scorer")
    g.add_edge("repro_scorer", "synthesizer")
    g.add_edge("synthesizer",  END)

    return g.compile()


# ── Pipeline 2: PDF upload (5 agents) ─────────────────────────────────────────

def _build_pdf_graph():
    g = StateGraph(ResearchState)

    # Same nodes as above — they read state fields, not the pipeline they're in
    g.add_node("critic",       critic_node)
    g.add_node("hypothesis",   hypothesis_node)
    g.add_node("memory",       memory_node)
    g.add_node("repro_scorer", repro_scorer_node)
    g.add_node("synthesizer",  synthesizer_node)

    g.set_entry_point("critic")           # jump straight to critique
    g.add_edge("critic",       "hypothesis")
    g.add_edge("hypothesis",   "memory")
    g.add_edge("memory",       "repro_scorer")
    g.add_edge("repro_scorer", "synthesizer")
    g.add_edge("synthesizer",  END)

    return g.compile()


# Compile once at startup — these objects are reused for every request
pipeline     = _build_arxiv_graph()
pdf_pipeline = _build_pdf_graph()


# ── Public runner functions ────────────────────────────────────────────────────

def run_pipeline(query: str) -> dict:
    """
    Run the full 7-agent arXiv pipeline.

    Args:
        query: Raw research topic from the user.

    Returns:
        Completed ResearchState dict.
    """
    initial_state: ResearchState = {
        "query":         query,
        "refined_query": "",
        "papers":        [],
        "critique":      "",
        "hypotheses":    [],
        "key_findings":  [],
        "repro_scores":  [],
        "synthesis":     "",
        "errors":        [],
    }
    return pipeline.invoke(initial_state)


def run_pdf_pipeline(paper: dict) -> dict:
    """
    Run the 5-agent PDF pipeline for a single uploaded paper.

    Args:
        paper: Dict returned by app.utils.pdf_parser.parse_pdf().
               Must include at minimum: title, abstract, full_text.

    Returns:
        Completed ResearchState dict (papers, critique, hypotheses,
        key_findings, repro_scores, synthesis, errors).
    """
    initial_state: ResearchState = {
        # Use the paper title as the "query" so agents have a topic anchor
        "query":         paper.get("title", "Uploaded Paper"),
        "refined_query": paper.get("title", ""),
        "papers":        [paper],    # pre-populate — no Research agent needed
        "critique":      "",
        "hypotheses":    [],
        "key_findings":  [],
        "repro_scores":  [],
        "synthesis":     "",
        "errors":        [],
    }
    return pdf_pipeline.invoke(initial_state)

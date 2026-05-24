"""
app/agents/graph.py — LangGraph pipelines for ResearchPilot AI.

Pipeline 1 — arXiv mode (9 agents):
  Planner → Research → Critic → Hypothesis ⟲ Evaluator
  → Memory → ReproScorer → TechAnalyzer → Synthesizer

Pipeline 2 — PDF mode (7 agents):
  Critic → Hypothesis ⟲ Evaluator
  → Memory → ReproScorer → TechAnalyzer → Synthesizer

The ⟲ symbol means the Evaluator can loop back to Hypothesis (max 2×).
"""

from langgraph.graph import StateGraph, END

from app.agents.state                import ResearchState
from app.agents.planner              import planner_node
from app.agents.research             import research_node
from app.agents.critic               import critic_node
from app.agents.hypothesis           import hypothesis_node
from app.agents.hypothesis_evaluator import hypothesis_evaluator_node
from app.agents.memory               import memory_node
from app.agents.repro_scorer         import repro_scorer_node
from app.agents.tech_analyzer        import tech_analyzer_node
from app.agents.synthesizer          import synthesizer_node


# ── Router: decides whether to loop back or move forward ──────────────────────

def route_after_evaluator(state: ResearchState) -> str:
    if state.get("hypothesis_quality") == "retry":
        print("[Router] Retry — sending back to Hypothesis.")
        return "hypothesis"
    print("[Router] Pass — moving forward to Memory.")
    return "memory"


# ── Pipeline 1: arXiv (9 agents) ──────────────────────────────────────────────

def _build_arxiv_graph():
    g = StateGraph(ResearchState)

    g.add_node("planner",              planner_node)
    g.add_node("research",             research_node)
    g.add_node("critic",               critic_node)
    g.add_node("hypothesis",           hypothesis_node)
    g.add_node("hypothesis_evaluator", hypothesis_evaluator_node)
    g.add_node("memory",               memory_node)
    g.add_node("repro_scorer",         repro_scorer_node)
    g.add_node("tech_analyzer",        tech_analyzer_node)
    g.add_node("synthesizer",          synthesizer_node)

    g.set_entry_point("planner")
    g.add_edge("planner",              "research")
    g.add_edge("research",             "critic")
    g.add_edge("critic",               "hypothesis")
    g.add_edge("hypothesis",           "hypothesis_evaluator")
    g.add_conditional_edges(
        "hypothesis_evaluator", route_after_evaluator,
        {"hypothesis": "hypothesis", "memory": "memory"},
    )
    g.add_edge("memory",               "repro_scorer")
    g.add_edge("repro_scorer",         "tech_analyzer")
    g.add_edge("tech_analyzer",        "synthesizer")
    g.add_edge("synthesizer",          END)

    return g.compile()


# ── Pipeline 2: PDF (7 agents) ────────────────────────────────────────────────

def _build_pdf_graph():
    g = StateGraph(ResearchState)

    g.add_node("critic",               critic_node)
    g.add_node("hypothesis",           hypothesis_node)
    g.add_node("hypothesis_evaluator", hypothesis_evaluator_node)
    g.add_node("memory",               memory_node)
    g.add_node("repro_scorer",         repro_scorer_node)
    g.add_node("tech_analyzer",        tech_analyzer_node)
    g.add_node("synthesizer",          synthesizer_node)

    g.set_entry_point("critic")
    g.add_edge("critic",               "hypothesis")
    g.add_edge("hypothesis",           "hypothesis_evaluator")
    g.add_conditional_edges(
        "hypothesis_evaluator", route_after_evaluator,
        {"hypothesis": "hypothesis", "memory": "memory"},
    )
    g.add_edge("memory",               "repro_scorer")
    g.add_edge("repro_scorer",         "tech_analyzer")
    g.add_edge("tech_analyzer",        "synthesizer")
    g.add_edge("synthesizer",          END)

    return g.compile()


# Compile once — reused for every request
pipeline     = _build_arxiv_graph()
pdf_pipeline = _build_pdf_graph()


# ── Public runners ─────────────────────────────────────────────────────────────

def run_pipeline(query: str) -> dict:
    return pipeline.invoke({
        "query":                 query,
        "refined_query":         "",
        "papers":                [],
        "critique":              "",
        "hypotheses":            [],
        "hypothesis_iterations": 0,
        "hypothesis_quality":    "",
        "evaluator_feedback":    "",
        "key_findings":          [],
        "repro_scores":          [],
        "model_profiles":        [],
        "code_snippet":          "",
        "methodology":           [],
        "assumptions":           [],
        "weaknesses":            [],
        "synthesis":             "",
        "errors":                [],
    })


def run_pdf_pipeline(paper: dict) -> dict:
    return pdf_pipeline.invoke({
        "query":                 paper.get("title", "Uploaded Paper"),
        "refined_query":         paper.get("title", ""),
        "papers":                [paper],
        "critique":              "",
        "hypotheses":            [],
        "hypothesis_iterations": 0,
        "hypothesis_quality":    "",
        "evaluator_feedback":    "",
        "key_findings":          [],
        "repro_scores":          [],
        "model_profiles":        [],
        "code_snippet":          "",
        "methodology":           [],
        "assumptions":           [],
        "weaknesses":            [],
        "synthesis":             "",
        "errors":                [],
    })

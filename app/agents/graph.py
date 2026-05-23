"""
app/agents/graph.py — LangGraph pipelines for ResearchPilot AI.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS A CONDITIONAL EDGE? (beginner explanation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A normal (fixed) edge always goes from A → B.

A conditional edge is an IF statement built into the graph:
  "After node A finishes, call a router function.
   If the router returns 'X', go to node X.
   If it returns 'Y', go to node Y."

Phase 5 adds this conditional edge after the Evaluator:

  Hypothesis → Evaluator ──┬── verdict="retry" → Hypothesis (loop back)
                            └── verdict="pass"  → Memory (continue forward)

This creates the feedback loop.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pipeline 1 (arXiv — 8 nodes now):
  Planner → Research → Critic → Hypothesis ⟲ Evaluator → Memory → ReproScorer → Synthesizer

Pipeline 2 (PDF — 6 nodes now):
  Critic → Hypothesis ⟲ Evaluator → Memory → ReproScorer → Synthesizer
"""

from langgraph.graph import StateGraph, END

from app.agents.state               import ResearchState
from app.agents.planner             import planner_node
from app.agents.research            import research_node
from app.agents.critic              import critic_node
from app.agents.hypothesis          import hypothesis_node
from app.agents.hypothesis_evaluator import hypothesis_evaluator_node
from app.agents.memory              import memory_node
from app.agents.repro_scorer        import repro_scorer_node
from app.agents.synthesizer         import synthesizer_node


# ── Router function (shared by both pipelines) ────────────────────────────────

def route_after_evaluator(state: ResearchState) -> str:
    """
    This function is called by LangGraph after the Evaluator node finishes.
    It reads the state and returns a STRING that tells LangGraph which node
    to visit next.

    Think of it as a traffic light at a junction:
      RED   (retry) → turn around, go back to Hypothesis
      GREEN (pass)  → continue forward to Memory

    LangGraph maps the returned string to an actual node name using the
    `path_map` dict in add_conditional_edges() below.
    """
    quality = state.get("hypothesis_quality", "pass")

    if quality == "retry":
        print("[Router] Verdict: RETRY — sending back to Hypothesis.")
        return "hypothesis"    # key in path_map → hypothesis node

    print("[Router] Verdict: PASS — moving forward to Memory.")
    return "memory"            # key in path_map → memory node


# ── Pipeline 1: arXiv research (8 agents) ─────────────────────────────────────

def _build_arxiv_graph():
    g = StateGraph(ResearchState)

    # Register all 8 nodes
    g.add_node("planner",              planner_node)
    g.add_node("research",             research_node)
    g.add_node("critic",               critic_node)
    g.add_node("hypothesis",           hypothesis_node)
    g.add_node("hypothesis_evaluator", hypothesis_evaluator_node)
    g.add_node("memory",               memory_node)
    g.add_node("repro_scorer",         repro_scorer_node)
    g.add_node("synthesizer",          synthesizer_node)

    # Fixed (always-run) edges
    g.set_entry_point("planner")
    g.add_edge("planner",              "research")
    g.add_edge("research",             "critic")
    g.add_edge("critic",               "hypothesis")
    g.add_edge("hypothesis",           "hypothesis_evaluator")

    # ── Conditional edge — the feedback loop ──────────────────────────────
    g.add_conditional_edges(
        "hypothesis_evaluator",   # FROM: run this node first
        route_after_evaluator,    # THEN: call this function to decide next step
        {
            # The function returns one of these strings:
            "hypothesis": "hypothesis",   # → loop back
            "memory":     "memory",       # → continue forward
        },
    )
    # ─────────────────────────────────────────────────────────────────────

    g.add_edge("memory",               "repro_scorer")
    g.add_edge("repro_scorer",         "synthesizer")
    g.add_edge("synthesizer",          END)

    return g.compile()


# ── Pipeline 2: PDF upload (6 agents) ─────────────────────────────────────────

def _build_pdf_graph():
    g = StateGraph(ResearchState)

    g.add_node("critic",               critic_node)
    g.add_node("hypothesis",           hypothesis_node)
    g.add_node("hypothesis_evaluator", hypothesis_evaluator_node)
    g.add_node("memory",               memory_node)
    g.add_node("repro_scorer",         repro_scorer_node)
    g.add_node("synthesizer",          synthesizer_node)

    g.set_entry_point("critic")
    g.add_edge("critic",               "hypothesis")
    g.add_edge("hypothesis",           "hypothesis_evaluator")

    # Same conditional edge — feedback loop works identically in PDF mode
    g.add_conditional_edges(
        "hypothesis_evaluator",
        route_after_evaluator,
        {
            "hypothesis": "hypothesis",
            "memory":     "memory",
        },
    )

    g.add_edge("memory",               "repro_scorer")
    g.add_edge("repro_scorer",         "synthesizer")
    g.add_edge("synthesizer",          END)

    return g.compile()


# Compile once at startup — reused for every request
pipeline     = _build_arxiv_graph()
pdf_pipeline = _build_pdf_graph()


# ── Public runner functions ────────────────────────────────────────────────────

def run_pipeline(query: str) -> dict:
    """Run the full arXiv pipeline (8 agents + optional feedback loop)."""
    initial_state: ResearchState = {
        "query":                  query,
        "refined_query":          "",
        "papers":                 [],
        "critique":               "",
        "hypotheses":             [],
        # Phase 5 additions — start at zero / empty
        "hypothesis_iterations":  0,
        "hypothesis_quality":     "",
        "evaluator_feedback":     "",
        "key_findings":           [],
        "repro_scores":           [],
        "synthesis":              "",
        "errors":                 [],
    }
    return pipeline.invoke(initial_state)


def run_pdf_pipeline(paper: dict) -> dict:
    """Run the PDF pipeline (6 agents + optional feedback loop)."""
    initial_state: ResearchState = {
        "query":                  paper.get("title", "Uploaded Paper"),
        "refined_query":          paper.get("title", ""),
        "papers":                 [paper],
        "critique":               "",
        "hypotheses":             [],
        "hypothesis_iterations":  0,
        "hypothesis_quality":     "",
        "evaluator_feedback":     "",
        "key_findings":           [],
        "repro_scores":           [],
        "synthesis":              "",
        "errors":                 [],
    }
    return pdf_pipeline.invoke(initial_state)

"""
app/agents/hypothesis.py — Hypothesis Agent

Role: Reads the Critic's identified weaknesses and generates concrete,
      testable research hypotheses that a scientist could actually pursue.

This is one of the most valuable agents — it turns "what's missing" into
"what you could do next."

Input state fields:  query, critique
Output state fields: hypotheses (list of strings)
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


SYSTEM_PROMPT = """You are a creative research scientist who specialises in
generating novel, testable hypotheses from identified research gaps.

Given a research topic and a critique of current literature, generate exactly
5 testable hypotheses. Each hypothesis must:
  • Start with "H: "
  • Be a single, specific, falsifiable statement (not a question).
  • Suggest a concrete experiment or measurement that could test it.
  • Be novel — do not simply restate what existing papers already do.

Output ONLY the 5 hypotheses, one per line. No preamble, no numbering.
"""


def hypothesis_node(state: ResearchState) -> dict:
    """Generate testable hypotheses from the critique."""
    critique = state.get("critique", "")

    if not critique or critique.startswith("No papers"):
        return {
            "hypotheses": ["Insufficient data to generate hypotheses."],
            "errors": state.get("errors", []) + ["Hypothesis: skipped — no critique."],
        }

    print("[Hypothesis] Generating hypotheses…")

    user_message = (
        f"Research topic: {state['query']}\n\n"
        f"Critique of current literature:\n{critique}"
    )

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])
        raw = response.content.strip()
        # Split on newlines and keep only lines that start with "H: "
        hypotheses = [
            line.strip()
            for line in raw.splitlines()
            if line.strip().startswith("H: ")
        ]
        # Fallback: if the model forgot the prefix, keep all non-empty lines
        if not hypotheses:
            hypotheses = [line.strip() for line in raw.splitlines() if line.strip()]
    except Exception as e:
        hypotheses = ["Could not generate hypotheses."]
        return {"hypotheses": hypotheses, "errors": state.get("errors", []) + [f"Hypothesis: {e}"]}

    print(f"[Hypothesis] Generated {len(hypotheses)} hypotheses.")
    return {"hypotheses": hypotheses}

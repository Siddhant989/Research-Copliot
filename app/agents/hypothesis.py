"""
app/agents/hypothesis.py — Hypothesis Agent

Role: Generates 5 testable hypotheses from the Critic's identified gaps.

Phase 5 upgrade: this agent now runs in two modes:
  • FIRST RUN  (hypothesis_iterations == 0)
      Normal generation from the critique alone.

  • RETRY RUN  (hypothesis_iterations > 0, evaluator_feedback is set)
      The Evaluator rejected the previous batch.  The agent re-reads its
      own previous output + the evaluator's written feedback, then writes
      an improved set.  This is the "feedback loop" in action.

Input state fields:  query, critique, hypothesis_iterations, evaluator_feedback
Output state fields: hypotheses, hypothesis_iterations
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


# ── System prompts — one for each mode ────────────────────────────────────────

FIRST_RUN_PROMPT = """You are a creative research scientist who specialises in
generating novel, testable hypotheses from identified research gaps.

Given a research topic and a critique of current literature, generate exactly
5 testable hypotheses. Each hypothesis must:
  • Start with "H: "
  • Be a single, specific, falsifiable statement (not a question).
  • Name a concrete variable, model, dataset, or metric to measure.
  • Suggest how it could be tested (experiment, comparison, measurement).
  • Be novel — do not simply restate what existing papers already do.

Output ONLY the 5 hypotheses, one per line. No preamble, no numbering.
"""

RETRY_PROMPT = """You are a research scientist who must IMPROVE a rejected set
of hypotheses based on an evaluator's feedback.

Read the feedback carefully — it tells you exactly what was wrong.
Then generate 5 NEW hypotheses that directly address the criticism.

Each hypothesis must:
  • Start with "H: "
  • Be a single, specific, falsifiable statement.
  • Name a concrete variable, model, dataset, or metric.
  • Suggest how it could be tested.
  • Be clearly different from and better than the rejected ones.

Output ONLY the 5 hypotheses, one per line. No preamble, no numbering.
"""


def _parse_hypotheses(raw: str) -> list:
    """Extract hypothesis lines from raw LLM output."""
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    # Prefer lines that start with the required "H: " prefix
    tagged = [l for l in lines if l.startswith("H: ")]
    return tagged if tagged else lines   # fallback: keep all non-empty lines


def hypothesis_node(state: ResearchState) -> dict:
    """
    Generate (or re-generate) hypotheses.

    Each time this node runs, it increments hypothesis_iterations so the
    Evaluator and the graph router can track how many attempts have been made.
    """
    critique   = state.get("critique", "")
    iterations = state.get("hypothesis_iterations", 0)   # 0 on first call
    feedback   = state.get("evaluator_feedback", "")

    if not critique or critique.startswith("No papers"):
        return {
            "hypotheses":             ["Insufficient data to generate hypotheses."],
            "hypothesis_iterations":  iterations + 1,
            "errors": state.get("errors", []) + ["Hypothesis: skipped — no critique."],
        }

    is_retry = iterations > 0 and bool(feedback)

    if is_retry:
        print(f"[Hypothesis] RETRY #{iterations} — incorporating evaluator feedback…")
        system_prompt = RETRY_PROMPT
        user_message  = (
            f"Research topic: {state['query']}\n\n"
            f"Critique of current literature:\n{critique}\n\n"
            f"━━━ EVALUATOR FEEDBACK (what was wrong with previous hypotheses) ━━━\n"
            f"{feedback}\n\n"
            f"━━━ REJECTED HYPOTHESES (do NOT reuse these) ━━━\n"
            + "\n".join(state.get("hypotheses", []))
        )
    else:
        print("[Hypothesis] First run — generating hypotheses from critique…")
        system_prompt = FIRST_RUN_PROMPT
        user_message  = (
            f"Research topic: {state['query']}\n\n"
            f"Critique of current literature:\n{critique}"
        )

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])
        hypotheses = _parse_hypotheses(response.content)
    except Exception as e:
        hypotheses = ["Could not generate hypotheses."]
        return {
            "hypotheses":            hypotheses,
            "hypothesis_iterations": iterations + 1,
            "errors": state.get("errors", []) + [f"Hypothesis: {e}"],
        }

    print(f"[Hypothesis] Generated {len(hypotheses)} hypotheses (attempt {iterations + 1}).")
    return {
        "hypotheses":            hypotheses,
        "hypothesis_iterations": iterations + 1,   # always increment
    }

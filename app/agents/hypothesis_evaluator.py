"""
app/agents/hypothesis_evaluator.py — Hypothesis Evaluator Agent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT THIS AGENT DOES (beginner explanation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Imagine a professor grading student hypotheses.

The student (Hypothesis agent) writes 5 hypotheses.
The professor (this agent) reads them and asks:
  "Are these actually testable?  Are they specific?  Are they novel?"

If the answer is YES → verdict = "pass" → pipeline moves forward
If the answer is NO  → verdict = "retry" → the professor writes
  feedback and sends the student back to try again

LangGraph calls a "router function" after this node to decide
which path to take.  That routing logic lives in graph.py.

Maximum retries: 2  (safety guard — the loop can never run forever)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Input state fields:  hypotheses, hypothesis_iterations
Output state fields: hypothesis_quality, evaluator_feedback
"""

import json
import re

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm

# Hard limit — the loop can run at most this many times total
MAX_ITERATIONS = 2

SYSTEM_PROMPT = """You are a strict but fair research hypothesis evaluator.

You will receive a list of research hypotheses. Evaluate them as a group
against ALL four quality criteria below.

Quality criteria (ALL must be satisfied to PASS):
  1. SPECIFIC   — each hypothesis names a concrete variable, model, or metric.
                  BAD: "AI will improve healthcare."
                  GOOD: "Fine-tuning BERT on clinical notes will reduce ICD-10
                         coding errors by ≥15% vs. the baseline GPT-2 model."
  2. TESTABLE   — each hypothesis can be confirmed or refuted by a real
                  experiment or measurement.
  3. NOVEL      — hypotheses do not merely restate conclusions already drawn
                  in the papers provided.
  4. DIVERSE    — the hypotheses cover meaningfully different aspects of the
                  topic, not just variations of one idea.

Output ONLY this JSON (no markdown fences, no extra text):
{
  "verdict": "pass" or "retry",
  "feedback": "One short paragraph (3-5 sentences) explaining exactly what
               is weak and how the hypotheses should be improved.
               Use an empty string if verdict is pass."
}
"""


def hypothesis_evaluator_node(state: ResearchState) -> dict:
    """
    Grade the hypotheses.  If they fail, write feedback and mark for retry.
    The routing decision (loop vs continue) is made in graph.py, not here.
    """
    hypotheses = state.get("hypotheses", [])
    iterations = state.get("hypothesis_iterations", 0)

    # ── Safety guard: never loop more than MAX_ITERATIONS times ──────────
    # Even if quality is bad, we stop retrying after the limit.
    # This ensures the pipeline always completes.
    if iterations >= MAX_ITERATIONS:
        print(f"[Evaluator] Max iterations ({MAX_ITERATIONS}) reached — forcing pass.")
        return {
            "hypothesis_quality":  "pass",
            "evaluator_feedback":  "",
        }

    if not hypotheses:
        return {
            "hypothesis_quality":  "pass",   # nothing to evaluate
            "evaluator_feedback":  "",
        }

    print(f"[Evaluator] Grading {len(hypotheses)} hypotheses (iteration {iterations})…")

    hypotheses_text = "\n".join(
        f"  {i+1}. {h}" for i, h in enumerate(hypotheses)
    )
    user_message = (
        f"Research topic: {state.get('query', '')}\n\n"
        f"Hypotheses to evaluate:\n{hypotheses_text}"
    )

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])
        raw = response.content.strip()

        # Strip accidental markdown fences
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

        result = json.loads(raw)
        verdict  = result.get("verdict",  "pass")
        feedback = result.get("feedback", "")

    except Exception as e:
        # If the evaluator itself errors, don't block the pipeline — just pass
        print(f"[Evaluator] Error: {e} — defaulting to pass.")
        return {
            "hypothesis_quality":  "pass",
            "evaluator_feedback":  "",
            "errors": state.get("errors", []) + [f"Evaluator: {e}"],
        }

    if verdict == "retry":
        print(f"[Evaluator] RETRY requested. Feedback: {feedback[:80]}…")
    else:
        print("[Evaluator] PASS — hypotheses meet quality bar.")

    return {
        "hypothesis_quality":  verdict,
        "evaluator_feedback":  feedback,
    }

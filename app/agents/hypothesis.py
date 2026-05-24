"""
app/agents/hypothesis.py — Hypothesis Agent

Role: Turns the gaps found by the Critic into concrete ideas
      that a real researcher could actually go and test.

Plain-English tone — like a researcher pitching their next project
at a team meeting, not writing a grant proposal.

Input state fields:  query, critique, hypothesis_iterations, evaluator_feedback
Output state fields: hypotheses, hypothesis_iterations
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


FIRST_RUN_PROMPT = """You are a curious researcher who explains ideas as simply as possible.

Based on the gaps in the current literature, write exactly 5 research ideas.
Each idea must:
  • Start with "H: "
  • Be 2–3 sentences long
  • Sound like you're explaining it to a curious friend who is NOT a scientist
  • Answer three things naturally: What are you trying? Why does it matter? What would you find out?
  • Use everyday words — avoid acronyms, metric names, and jargon
  • Do NOT mention specific model names, dataset names, or percentage numbers

Good example (for AI + medicine):
  H: What if a small AI trained only on medical records could answer doctor questions
     better than a huge general-purpose AI? Most AI tools today learned from the whole
     internet — not specifically from medicine. This experiment would show whether
     focused training beats sheer scale for real-world health tasks.

Bad example:
  H: Fine-tuning a 7B LLaMA on MIMIC-III will yield 15% F1 gain on ICD-10 tasks.
  ← jargon-heavy, no plain explanation, unreadable to a first-time reader

Write only the 5 ideas, one per line. No intro, no numbering.
"""

RETRY_PROMPT = """You wrote 5 research ideas but they didn't pass review because they
were too technical and hard to understand for a first-time reader.

Here's the specific feedback — read it carefully before writing new ideas.

Now write 5 BETTER ideas that fix the exact problems mentioned.
Each idea must still:
  • Start with "H: "
  • Be written in plain everyday English — imagine explaining it to a smart friend
    who has never studied this topic
  • Be 2–3 sentences: what are you trying, why does it matter, what would you learn
  • Have NO jargon, acronyms, or technical metric names

Don't reuse the rejected ideas. Write fresh ones that address the feedback.
Write only the 5 ideas, one per line.
"""


def _parse_hypotheses(raw: str) -> list:
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    tagged = [l for l in lines if l.startswith("H: ")]
    return tagged if tagged else lines


def hypothesis_node(state: ResearchState) -> dict:
    critique   = state.get("critique", "")
    iterations = state.get("hypothesis_iterations", 0)
    feedback   = state.get("evaluator_feedback", "")

    if not critique or critique.startswith("No papers"):
        return {
            "hypotheses":            ["Not enough information to suggest research ideas."],
            "hypothesis_iterations": iterations + 1,
            "errors": state.get("errors", []) + ["Hypothesis: skipped — no critique."],
        }

    is_retry = iterations > 0 and bool(feedback)

    if is_retry:
        print(f"[Hypothesis] Retry #{iterations} — using evaluator feedback…")
        system_prompt = RETRY_PROMPT
        user_message  = (
            f"Research topic: {state['query']}\n\n"
            f"What the literature is missing:\n{critique}\n\n"
            f"WHY your previous ideas were rejected:\n{feedback}\n\n"
            f"Your rejected ideas (don't reuse these):\n"
            + "\n".join(state.get("hypotheses", []))
        )
    else:
        print("[Hypothesis] Generating research ideas…")
        system_prompt = FIRST_RUN_PROMPT
        user_message  = (
            f"Research topic: {state['query']}\n\n"
            f"What the literature is missing:\n{critique}"
        )

    try:
        response   = llm.invoke([SystemMessage(content=system_prompt),
                                  HumanMessage(content=user_message)])
        hypotheses = _parse_hypotheses(response.content)
    except Exception as e:
        hypotheses = ["Could not generate research ideas."]
        return {
            "hypotheses":            hypotheses,
            "hypothesis_iterations": iterations + 1,
            "errors": state.get("errors", []) + [f"Hypothesis: {e}"],
        }

    print(f"[Hypothesis] {len(hypotheses)} ideas generated (attempt {iterations + 1}).")
    return {"hypotheses": hypotheses, "hypothesis_iterations": iterations + 1}

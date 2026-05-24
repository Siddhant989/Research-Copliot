"""
app/agents/critic.py — Critic Agent

Role: Reads the fetched papers and surfaces what they're missing —
      in plain English, not academic-speak.

Think of this agent as a knowledgeable friend who read all the papers
and is now telling you honestly: "Here's what these papers don't cover,
and here's why that matters."

Input state fields:  query, papers
Output state fields: critique
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


SYSTEM_PROMPT = """You are a sharp, honest research reviewer — like a trusted
colleague who has read every paper and will tell you straight what's missing.

You'll get a research topic and summaries of several papers on that topic.

Your job: write 4-5 bullet points explaining what these papers are NOT doing well.
Write like you're talking to a smart colleague over coffee — clear, direct, no jargon.

For each bullet point:
  - Start with a short bold label (e.g. **The big gap they all ignore:**)
  - Then explain the problem in 2-3 plain sentences
  - Say WHY it matters in practice

Avoid: words like "methodological", "epistemological", "paradigmatic"
Use instead: "the way they test it", "how they set it up", "what they skip"

Focus only on what's MISSING or WEAK — don't summarise what the papers do.
"""


def _format_papers(papers: list) -> str:
    lines = []
    for i, p in enumerate(papers, 1):
        lines.append(
            f"{i}. {p['title']} ({p['published']})\n"
            f"   Summary: {p['abstract'][:400]}..."
        )
    return "\n\n".join(lines)


def critic_node(state: ResearchState) -> dict:
    papers = state.get("papers", [])
    if not papers:
        return {
            "critique": "No papers were found to review.",
            "errors": state.get("errors", []) + ["Critic: skipped — no papers."],
        }

    print(f"[Critic] Reviewing {len(papers)} papers…")

    user_message = (
        f"Research topic: {state['query']}\n\n"
        f"Papers to review:\n{_format_papers(papers)}"
    )

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])
        critique = response.content.strip()
    except Exception as e:
        critique = "Could not generate a critique."
        return {"critique": critique, "errors": state.get("errors", []) + [f"Critic: {e}"]}

    print("[Critic] Done.")
    return {"critique": critique}

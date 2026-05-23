"""
app/agents/critic.py — Critic Agent

Role: Reads the fetched papers and identifies:
      • Shared limitations / gaps across all papers
      • Methodological weaknesses
      • Datasets or settings that are under-explored

This critical analysis feeds directly into the Hypothesis Agent.

Input state fields:  query, papers
Output state fields: critique
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


SYSTEM_PROMPT = """You are a rigorous academic peer reviewer.
You will receive a research topic and abstracts of several papers on that topic.

Your task: write a focused critique (3-5 bullet points) that identifies:
1. Common limitations or blind spots across the papers.
2. Methodological weaknesses (e.g. small datasets, lack of baselines, biased evaluation).
3. Under-explored directions or missing comparisons.

Format your response as a bullet list. Be specific and constructive.
Do NOT summarise what the papers do — focus on what they FAIL to address.
"""


def _format_papers(papers: list) -> str:
    """Turn the paper list into a compact string for the prompt."""
    lines = []
    for i, p in enumerate(papers, 1):
        lines.append(
            f"{i}. [{p['title']}] ({p['published']})\n"
            f"   Abstract: {p['abstract'][:400]}..."
        )
    return "\n\n".join(lines)


def critic_node(state: ResearchState) -> dict:
    """Critique the fetched papers and surface weaknesses."""
    papers = state.get("papers", [])

    if not papers:
        return {
            "critique": "No papers were available to critique.",
            "errors": state.get("errors", []) + ["Critic: skipped — no papers."],
        }

    print(f"[Critic] Critiquing {len(papers)} papers…")

    user_message = (
        f"Research topic: {state['query']}\n\n"
        f"Papers:\n{_format_papers(papers)}"
    )

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])
        critique = response.content.strip()
    except Exception as e:
        critique = "Critique could not be generated."
        return {"critique": critique, "errors": state.get("errors", []) + [f"Critic: {e}"]}

    print("[Critic] Done.")
    return {"critique": critique}

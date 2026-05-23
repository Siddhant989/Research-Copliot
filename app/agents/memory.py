"""
app/agents/memory.py — Memory Agent

Role: Distils the most important, reusable findings from all fetched papers
      into a compact bullet-point list.  This acts as the "institutional memory"
      that the Synthesizer draws from when writing the final report.

In future phases this could persist findings to a vector database (e.g. ChromaDB)
so that insights from previous queries are recalled automatically.

Input state fields:  query, papers
Output state fields: key_findings (list of strings)
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


SYSTEM_PROMPT = """You are a research librarian who distils academic papers
into the most essential, reusable insights.

Given a research topic and several paper abstracts, extract exactly 6 key findings.
Each finding must:
  • Start with "• "
  • Be one sentence, self-contained, and factual.
  • Reference the finding's significance (why it matters).
  • NOT be a copy-paste from the abstract — paraphrase and synthesise.

Output ONLY the 6 bullet points, one per line.
"""


def _format_abstracts(papers: list) -> str:
    return "\n\n".join(
        f"Paper {i}: {p['title']}\nAbstract: {p['abstract'][:500]}"
        for i, p in enumerate(papers, 1)
    )


def memory_node(state: ResearchState) -> dict:
    """Extract and store key findings from the papers."""
    papers = state.get("papers", [])

    if not papers:
        return {
            "key_findings": ["No papers available to extract findings from."],
            "errors": state.get("errors", []) + ["Memory: skipped — no papers."],
        }

    print(f"[Memory] Extracting key findings from {len(papers)} papers…")

    user_message = (
        f"Research topic: {state['query']}\n\n"
        f"Papers:\n{_format_abstracts(papers)}"
    )

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])
        raw = response.content.strip()
        findings = [
            line.strip()
            for line in raw.splitlines()
            if line.strip().startswith("•")
        ]
        if not findings:
            findings = [line.strip() for line in raw.splitlines() if line.strip()]
    except Exception as e:
        findings = ["Could not extract key findings."]
        return {"key_findings": findings, "errors": state.get("errors", []) + [f"Memory: {e}"]}

    print(f"[Memory] Stored {len(findings)} findings.")
    return {"key_findings": findings}

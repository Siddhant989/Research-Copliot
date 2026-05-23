"""
app/agents/planner.py — Planner Agent

Role: Takes the raw user query and turns it into a better arXiv search query.
      Users often type conversational phrases ("tell me about X") that don't
      search well.  The Planner rewrites them into precise academic terms.

Input state fields:  query
Output state fields: refined_query
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


SYSTEM_PROMPT = """You are a research planning expert.
Your job is to rewrite a user's research topic into a concise, precise
arXiv search query (max 12 words) that will return the most relevant papers.

Rules:
- Use academic terminology, not conversational language.
- Include the core concept, method, and domain if present.
- Output ONLY the refined query — no explanation, no punctuation at the end.

Examples:
  User: "how does attention work in transformers"
  Output: transformer self-attention mechanism natural language processing

  User: "drug discovery with AI"
  Output: deep learning molecular property prediction drug discovery
"""


def planner_node(state: ResearchState) -> dict:
    """
    LangGraph node function.
    Receives the full state dict, returns a partial dict with new/updated fields.
    """
    print(f"[Planner] Refining query: '{state['query']}'")

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=state["query"]),
        ])
        refined = response.content.strip()
    except Exception as e:
        # Fall back to the original query so the pipeline keeps running
        refined = state["query"]
        return {"refined_query": refined, "errors": state.get("errors", []) + [f"Planner: {e}"]}

    print(f"[Planner] Refined: '{refined}'")
    return {"refined_query": refined}

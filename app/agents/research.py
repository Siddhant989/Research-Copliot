"""
app/agents/research.py — Research Agent

Role: Uses the Planner's refined query to fetch real papers from arXiv.
      This is the only agent that makes an external network call (to arXiv).

Input state fields:  refined_query
Output state fields: papers
"""

from app.agents.state import ResearchState
from app.utils.arxiv_fetcher import fetch_papers
import os


def research_node(state: ResearchState) -> dict:
    """Fetch papers from arXiv using the planner's refined query."""
    query = state.get("refined_query") or state.get("query", "")
    max_results = int(os.getenv("ARXIV_MAX_RESULTS", 5))

    print(f"[Research] Fetching up to {max_results} papers for: '{query}'")

    papers = fetch_papers(query, max_results=max_results)

    if not papers:
        return {
            "papers": [],
            "errors": state.get("errors", []) + ["Research: No papers found for this query."],
        }

    print(f"[Research] Found {len(papers)} papers.")
    return {"papers": papers}

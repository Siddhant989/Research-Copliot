import os
from pathlib import Path
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END

from graph.state import ResearchState
from agents.planner              import planner_node
from agents.research             import research_node
from agents.critic               import critic_node
from agents.hypothesis           import hypothesis_node
from agents.reproducibility_scorer import reproducibility_scorer_node
from agents.code_agent           import code_agent_node
from agents.evidence_tracker     import evidence_tracker_node
from agents.synthesizer          import synthesizer_node
from utils.arxiv_fetcher         import fetch_paper
from utils.pdf_parser            import parse_pdf, extract_figures


_ROOT = Path(__file__).parent.parent
load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT.parent / ".env")


def _collect_api_keys():
    numbered_keys = []
    for key_name, value in os.environ.items():
        if key_name.startswith("GEMINI_API_KEY_") and value.strip():
            numbered_keys.append(value)
    numbered_keys.sort()

    if numbered_keys:
        return numbered_keys

    # Fall back to a single key if no numbered ones are set
    single = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    if single.strip():
        return [single.strip()]
    return []


# Node 1: Paper Fetcher
def paper_fetcher_node(state: ResearchState) -> dict:
    if state.get("metadata") and state["metadata"].get("title"):
        return {}

    logs = list(state.get("agent_logs", []))
    query = state.get("paper_title", "") or state.get("arxiv_url", "")
    logs.append({"agent": "Paper Fetcher", "message": f"Searching for: {query[:60]}...","status": "running"})
    logs.append({"agent": "Paper Fetcher", "message": "Connecting to arXiv API...","status": "running"})

    try:
        paper = fetch_paper(query)
        logs.append({"agent": "Paper Fetcher", "message": f"✓ Found: {paper['title'][:50]}","status": "done"})
        return {
            "paper_title": paper["title"],
            "arxiv_url": paper.get("url", ""),
            "pdf_path": paper.get("pdf_path", ""),
            "abstract": paper.get("abstract", ""),
            "metadata": {
                "title": paper["title"],
                "authors": paper.get("authors", []),
                "year": paper.get("year", ""),
                "url": paper.get("url", ""),
                "arxiv_id": paper.get("arxiv_id", ""),
            },
            "agent_logs": logs,
        }
    except Exception as e:
        logs.append({"agent": "Paper Fetcher", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})
        return {"errors": [str(e)], "agent_logs": logs}



def pdf_extractor_node(state: ResearchState) -> dict:
    # Skip if text already extracted (resume path)
    if state.get("raw_text"):
        return {}

    logs = list(state.get("agent_logs", []))
    logs.append({"agent": "PDF Extractor", "message": "Opening PDF file...",         "status": "running"})
    logs.append({"agent": "PDF Extractor", "message": "Extracting text content...",  "status": "running"})

    pdf_path = state.get("pdf_path", "")
    if not pdf_path or not os.path.exists(pdf_path):
        logs.append({"agent": "PDF Extractor", "message": "⚠ No PDF available — using abstract only.","status": "error"})
        return {"raw_text": state.get("abstract", ""), "sections": {}, "agent_logs": logs}

    try:
        logs.append({"agent": "PDF Extractor", "message": "Parsing sections and structure...","status": "running"})
        parsed = parse_pdf(pdf_path)

        logs.append({"agent": "PDF Extractor", "message": "Extracting figures and diagrams...","status": "running"})
        try:
            figs = extract_figures(pdf_path)
        except Exception:
            figs = []

        logs.append({"agent": "PDF Extractor", "message": f"✓ Extracted {len(parsed['raw_text'])} chars, {len(figs)} figures.","status": "done"})
        return {
            "raw_text": parsed["raw_text"],
            "sections": parsed["sections"],
            "figures":  figs,
            "agent_logs": logs,
        }
    except Exception as e:
        logs.append({"agent": "PDF Extractor", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})
        return {"raw_text": state.get("abstract", ""), "sections": {}, "figures": [], "agent_logs": logs}



def _build_graph() -> StateGraph:
    g = StateGraph(ResearchState)

    g.add_node("paper_fetcher",          paper_fetcher_node)
    g.add_node("pdf_extractor",          pdf_extractor_node)
    g.add_node("planner",                planner_node)
    g.add_node("research",               research_node)
    g.add_node("critic",                 critic_node)
    g.add_node("hypothesis",             hypothesis_node)
    g.add_node("reproducibility_scorer", reproducibility_scorer_node)
    g.add_node("code_agent",             code_agent_node)
    g.add_node("evidence_tracker",       evidence_tracker_node)
    g.add_node("synthesizer",            synthesizer_node)

    g.set_entry_point("paper_fetcher")
    g.add_edge("paper_fetcher",          "pdf_extractor")
    g.add_edge("pdf_extractor",          "planner")
    g.add_edge("planner",                "research")
    g.add_edge("research",               "critic")
    g.add_edge("critic",                 "hypothesis")
    g.add_edge("hypothesis",             "reproducibility_scorer")
    g.add_edge("reproducibility_scorer", "code_agent")
    g.add_edge("code_agent",             "evidence_tracker")
    g.add_edge("evidence_tracker",       "synthesizer")
    g.add_edge("synthesizer",            END)

    return g.compile()


_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph



def run_pipeline(query: str) -> dict:
    initial: ResearchState = {
        "paper_title":              query,
        "arxiv_url":                query if "arxiv.org" in query else "",
        "pdf_path":                 None,
        "raw_text":                 "",
        "abstract":                 "",
        "sections":                 {},
        "metadata":                 {},
        "figures":                  [],
        "planner_output":           None,
        "research_output":          None,
        "critic_output":            None,
        "hypothesis_output":        None,
        "reproducibility_output":   None,
        "code_output":              None,
        "evidence_tracker_output":  None,
        "synthesizer_output":       None,
        "available_api_keys":       _collect_api_keys(),
        "exhausted_api_keys":       [],
        "pipeline_paused":          False,
        "agent_logs":               [],
        "errors":                   [],
    }
    graph = _get_graph()
    result = graph.invoke(initial)
    return {
        "state":  result,
        "paused": bool(result.get("pipeline_paused")),
    }


def resume_pipeline(paused_state: dict, new_api_key: str) -> dict:
    resume_state = dict(paused_state)
    resume_state["available_api_keys"] = [new_api_key.strip()]
    resume_state["pipeline_paused"]    = False
    # Keep exhausted_api_keys — don't retry spent keys

    graph = _get_graph()
    result = graph.invoke(resume_state)
    return {
        "state":  result,
        "paused": bool(result.get("pipeline_paused")),
    }

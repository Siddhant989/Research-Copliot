"""
graph/state.py — Shared LangGraph state passed between every agent node.
"""

from typing import TypedDict, Optional, List, Dict, Any


class ResearchState(TypedDict):
    # ── Input ──────────────────────────────────────────────────────────────────
    paper_title: str
    arxiv_url:   Optional[str]
    pdf_path:    Optional[str]

    # ── Extracted content ──────────────────────────────────────────────────────
    raw_text: str
    abstract: str
    sections: Dict[str, Any]
    metadata: Dict[str, Any]   # title, authors, year, categories, etc.
    figures:  Optional[List]   # [{page, caption, description, data, width, height}]

    # ── Agent outputs ──────────────────────────────────────────────────────────
    planner_output:          Optional[Dict]
    research_output:         Optional[Dict]
    critic_output:           Optional[Dict]
    hypothesis_output:       Optional[Dict]
    reproducibility_output:  Optional[Dict]
    code_output:             Optional[Dict]
    evidence_tracker_output: Optional[List]
    synthesizer_output:      Optional[Dict]

    # ── API-key pool (managed by utils/llm_manager.py) ────────────────────────
    available_api_keys: List[str]   # keys still usable in this run
    exhausted_api_keys: List[str]   # keys that hit quota — never retried

    # ── Pipeline control ───────────────────────────────────────────────────────
    pipeline_paused: Optional[bool]  # True when all keys exhausted mid-run

    # ── Pipeline telemetry ─────────────────────────────────────────────────────
    agent_logs: List[Dict]   # [{agent, message, timestamp, status}]
    errors:     List[str]

# agents/evidence_tracker.py — Node 10: Evidence Tracker Agent
# Traces every major agent claim back to a specific location in the paper PDF.

import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_list


SYSTEM_PROMPT = """You are a meticulous Evidence Specialist. For every important claim
made by any agent, you find its exact supporting evidence in the paper text.

Return ONLY a valid JSON array (no markdown fences):
[
  {{
    "claim": "Plain English statement of the claim",
    "agent_source": "Which agent made this claim (Planner/Research/Critic/etc.)",
    "page_number": "e.g. '3' or '3-4' or 'Abstract'",
    "section": "Section name (e.g. '4.2 Experimental Setup')",
    "supporting_quote": "Near-exact quote from the paper (1-2 sentences) supporting this claim"
  }}
]

Generate 7-8 evidence entries covering the most important claims across all agents."""

HUMAN_TEMPLATE = """Trace these claims to their evidence in the paper.

Paper: {title}
Full text (with page markers): {raw_text}

Claims to trace:
- Planner: {planner_claims}
- Research: {research_claims}
- Critic: {critic_claims}
- Reproducibility: {repro_claims}"""


def evidence_tracker_node(state):
    # Skip if pipeline was paused upstream
    if state.get("pipeline_paused"):
        return {}
    # Skip if already computed — non-empty list means done (resume path)
    if state.get("evidence_tracker_output"):
        return {}

    logs     = list(state.get("agent_logs", []))
    planner  = state.get("planner_output",         {}) or {}
    critic   = state.get("critic_output",          {}) or {}
    research = state.get("research_output",        {}) or {}
    repro    = state.get("reproducibility_output", {}) or {}

    logs.append({"agent": "Evidence", "message": "Tracing claims to source...",   "status": "running"})
    logs.append({"agent": "Evidence", "message": "Extracting page references...","status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    # Build claim strings to send to the LLM
    planner_claims  = planner.get("novelty_claim", "") + " | " + planner.get("research_objective", "")
    research_claims = research.get("how_paper_improves", "")
    critic_claims_parts = []
    for w in critic.get("weaknesses", [])[:3]:
        if isinstance(w, dict):
            critic_claims_parts.append(w.get("issue", ""))
        else:
            critic_claims_parts.append(str(w))
    critic_claims = " | ".join(critic_claims_parts)
    repro_claims  = repro.get("verdict", "")

    key_update = {}
    try:
        logs.append({"agent": "Evidence", "message": "Building evidence map...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":           title,
            "raw_text":        state.get("raw_text", "")[:5000],
            "planner_claims":  planner_claims,
            "research_claims": research_claims,
            "critic_claims":   critic_claims,
            "repro_claims":    repro_claims,
        })
        result = parse_json_list(content)
        logs.append({"agent": "Evidence", "message": "✓ Evidence map complete.","status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Evidence", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "evidence_tracker_output": [],
            "agent_logs":              logs,
            "available_api_keys":      e.available,
            "exhausted_api_keys":      e.exhausted,
            "pipeline_paused":         True,
        }
    except Exception as e:
        result = []
        logs.append({"agent": "Evidence", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"evidence_tracker_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

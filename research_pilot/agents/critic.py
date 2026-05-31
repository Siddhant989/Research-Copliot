# agents/critic.py — Node 5: Critic Agent
# Identifies weaknesses, hidden assumptions, missing experiments, and reproducibility risks.

import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """You are a skeptical Scientific Reviewer who rigorously critiques papers.
You find real problems — not minor nitpicks. Be specific and honest.

Return ONLY valid JSON (no markdown fences):
{{
  "weaknesses": [
    {{"issue": "Specific weakness", "impact": "Why this matters for the field", "severity": "high/medium/low"}}
  ],
  "assumptions": [
    {{"assumption": "What the paper assumes is true without proof", "risk": "What breaks if this is wrong"}}
  ],
  "missing_experiments": [
    {{"experiment": "What should have been tested", "reason": "Why this is important"}}
  ],
  "scalability_issues": [
    "Specific scalability problem — e.g. O(n²) attention complexity"
  ],
  "reproducibility_risks": [
    "Specific barrier to reproducing results"
  ],
  "strongest_weakness": "The single most important flaw in this paper (2 sentences)",
  "fairness_note": "One genuine strength even the critic admits (1 sentence)"
}}"""

HUMAN_TEMPLATE = """Critically evaluate this paper. Find real weaknesses, not surface-level ones.

Paper: {title}
Abstract: {abstract}
Methodology (from Planner): {planner_output}
Background (from Research Agent): {research_output}
Full text excerpt: {content}"""


def critic_node(state):
    # Skip if pipeline was paused upstream
    if state.get("pipeline_paused"):
        return {}
    # Skip if already computed (resume path)
    if state.get("critic_output"):
        return {}

    logs = list(state.get("agent_logs", []))
    logs.append({"agent": "Critic", "message": "Evaluating methodology robustness...","status": "running"})
    logs.append({"agent": "Critic", "message": "Detecting scalability limitations...","status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    key_update = {}
    try:
        logs.append({"agent": "Critic", "message": "Identifying missing baselines...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":           title,
            "abstract":        state.get("abstract",     "")[:1500],
            "planner_output":  json.dumps(state.get("planner_output",  {})),
            "research_output": json.dumps(state.get("research_output", {})),
            "content":         state.get("raw_text",     "")[:4000],
        })
        result = parse_json_response(content)
        logs.append({"agent": "Critic", "message": "✓ Critical review complete.","status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Critic", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "critic_output":      {},
            "agent_logs":         logs,
            "available_api_keys": e.available,
            "exhausted_api_keys": e.exhausted,
            "pipeline_paused":    True,
        }
    except Exception as e:
        result = {}
        logs.append({"agent": "Critic", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"critic_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

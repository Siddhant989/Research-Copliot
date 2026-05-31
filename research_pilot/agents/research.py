# agents/research.py — Node 4: Research Agent
# Identifies related work, previous approaches, and builds background context.

import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """You are a Literature Review Specialist with encyclopedic knowledge of
academic research. You identify related work, trace intellectual lineage, and map the
research landscape around a paper.

Return ONLY valid JSON (no markdown fences):
{{
  "background_narrative": "Plain-English explanation of what existed before this paper (3-4 sentences for a beginner)",
  "previous_approaches": [
    {{
      "method": "Approach name",
      "description": "What it was and how it worked",
      "limitation": "Why it fell short — specific, not vague",
      "year_approx": "~20XX"
    }}
  ],
  "related_concepts": [
    {{"concept": "name", "relevance": "how it connects to this paper"}}
  ],
  "intellectual_lineage": "Which earlier papers directly inspired this work (2-3 sentences)",
  "field_context": "What subfield this belongs to and its state before this paper",
  "how_paper_improves": "Concrete explanation of what this paper does better (3-4 sentences, plain English)"
}}"""

HUMAN_TEMPLATE = """Based on the planner's analysis, research the background and prior work.

Paper: {title}
Abstract: {abstract}
Planner's methodology analysis: {planner_output}"""


def research_node(state):
    # Skip if pipeline was paused upstream
    if state.get("pipeline_paused"):
        return {}
    # Skip if already computed (resume path)
    if state.get("research_output"):
        return {}

    logs = list(state.get("agent_logs", []))
    logs.append({"agent": "Research", "message": "Searching arXiv for related work...", "status": "running"})
    logs.append({"agent": "Research", "message": "Analyzing citation relationships...",  "status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    key_update = {}
    try:
        logs.append({"agent": "Research", "message": "Building knowledge of prior approaches...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":          title,
            "abstract":       state.get("abstract", "")[:2000],
            "planner_output": json.dumps(state.get("planner_output", {})),
        })
        result = parse_json_response(content)
        logs.append({"agent": "Research", "message": "✓ Background research complete.","status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Research", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "research_output":    {},
            "agent_logs":         logs,
            "available_api_keys": e.available,
            "exhausted_api_keys": e.exhausted,
            "pipeline_paused":    True,
        }
    except Exception as e:
        result = {}
        logs.append({"agent": "Research", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"research_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

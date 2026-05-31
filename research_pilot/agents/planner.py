# agents/planner.py — Node 3: Planner Agent
# Reads the paper and creates a structured research plan for all other agents.

from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """You are a Senior Research Strategist with deep expertise in analyzing
academic papers. Your job is to read a paper and create a structured execution plan that
other specialist agents will follow.

Return ONLY valid JSON (no markdown fences) with this structure:
{{
  "research_objective": "The core goal this paper tries to achieve (2-3 sentences)",
  "problem_statement": "The exact problem being solved (plain English)",
  "methodology_components": [
    {{"component": "name", "description": "what it does", "importance": "high/medium/low"}}
  ],
  "datasets": [
    {{"name": "dataset name", "size": "scale", "task": "what used for", "public": true}}
  ],
  "evaluation_metrics": [
    {{"metric": "name", "description": "what it measures"}}
  ],
  "task_decomposition": [
    "Task 1 for downstream agents",
    "Task 2...",
    "Task 3..."
  ],
  "execution_strategy": "Overall strategy summary (2-3 sentences)",
  "paper_type": "empirical/theoretical/survey/system",
  "novelty_claim": "What the paper claims is new"
}}"""

HUMAN_TEMPLATE = """Analyze this research paper and create the execution plan.

Paper Title: {title}
Abstract: {abstract}
Content excerpt: {content}"""


def planner_node(state):
    # Skip if the pipeline was paused upstream due to API key exhaustion
    if state.get("pipeline_paused"):
        return {}
    # Skip if this node already ran (happens when resuming a paused pipeline)
    if state.get("planner_output"):
        return {}

    logs = list(state.get("agent_logs", []))
    logs.append({"agent": "Planner", "message": "Reading abstract...",               "status": "running"})
    logs.append({"agent": "Planner", "message": "Identifying research objectives...","status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    # Get the paper title from metadata or fallback to the raw query
    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    key_update = {}
    try:
        logs.append({"agent": "Planner", "message": "Breaking methodology into components...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":    title,
            "abstract": state.get("abstract", "")[:2000],
            "content":  state.get("raw_text",  "")[:4000],
        })
        result = parse_json_response(content)
        logs.append({"agent": "Planner", "message": "Extracting evaluation pipeline...","status": "running"})
        logs.append({"agent": "Planner", "message": "✓ Execution plan ready.",          "status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Planner", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "planner_output":     {},
            "agent_logs":         logs,
            "available_api_keys": e.available,
            "exhausted_api_keys": e.exhausted,
            "pipeline_paused":    True,
        }
    except Exception as e:
        result = {}
        logs.append({"agent": "Planner", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"planner_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

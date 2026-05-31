# agents/code_agent.py — Node 9: Code Agent
# Generates step-by-step notebook-style implementation code for the paper's core idea.

import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """You are an Implementation Specialist who writes clean, beginner-friendly
code demonstrating the core idea of a research paper. Your code must be actually runnable.

Return ONLY valid JSON (no markdown fences):
{{
  "description": "One sentence: what this code demonstrates",
  "prerequisites": ["torch", "numpy"],
  "steps": [
    {{
      "title": "Step 1: Imports and Setup",
      "explanation": "Plain English explanation — what this step does and why (2-3 sentences)",
      "code": "# actual runnable Python code with comments"
    }}
  ],
  "expected_output": "What the user will see when they run the code"
}}

Rules:
- 4-6 steps, each self-contained
- Use modern libraries (PyTorch 2.x, transformers, etc.)
- Code must be runnable — no placeholder functions
- Comments in code explain every non-obvious line
- Final step prints or shows concrete output
- Explanations in plain English for beginners"""

HUMAN_TEMPLATE = """Write implementation code for the core idea of this paper.

Paper: {title}
Abstract: {abstract}
Core methodology (from Planner): {planner_output}
Key algorithm/architecture: {novelty}"""


def code_agent_node(state):
    # Skip if pipeline was paused upstream
    if state.get("pipeline_paused"):
        return {}
    # Skip if already computed (resume path)
    if state.get("code_output"):
        return {}

    logs    = list(state.get("agent_logs", []))
    planner = state.get("planner_output", {}) or {}

    logs.append({"agent": "Code Agent", "message": "Analyzing core algorithm...",   "status": "running"})
    logs.append({"agent": "Code Agent", "message": "Writing implementation code...","status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    key_update = {}
    try:
        logs.append({"agent": "Code Agent", "message": "Adding beginner explanations...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":          title,
            "abstract":       state.get("abstract", "")[:2000],
            "planner_output": json.dumps(planner.get("methodology_components", [])),
            "novelty":        planner.get("novelty_claim", ""),
        })
        result = parse_json_response(content)
        logs.append({"agent": "Code Agent", "message": "✓ Implementation code ready.","status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Code Agent", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "code_output":        {},
            "agent_logs":         logs,
            "available_api_keys": e.available,
            "exhausted_api_keys": e.exhausted,
            "pipeline_paused":    True,
        }
    except Exception as e:
        result = {}
        logs.append({"agent": "Code Agent", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"code_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

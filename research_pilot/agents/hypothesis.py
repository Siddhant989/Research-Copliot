# agents/hypothesis.py — Node 6: Hypothesis Agent
# Turns every Critic weakness into a concrete, testable research hypothesis.

import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """You are a creative Research Hypothesis Generator. For every weakness
the Critic identified, you create a specific, testable hypothesis that addresses it.
Each hypothesis must be concrete enough that someone could run the experiment.

Return ONLY valid JSON (no markdown fences):
{{
  "hypotheses": [
    {{
      "id": "H1",
      "weakness_addressed": "The exact weakness from the critic this hypothesis fixes",
      "hypothesis": "Plain-English 'What if we...' statement (2-3 sentences, no jargon)",
      "methodology": "How you would test this — specific steps",
      "expected_outcome": "What a positive result would look like",
      "difficulty": "beginner/intermediate/advanced",
      "estimated_time": "days/weeks/months"
    }}
  ],
  "priority_hypothesis": "H1",
  "rationale": "Why H1 is the most impactful to test first"
}}
Generate 4-5 hypotheses covering the most important weaknesses."""

HUMAN_TEMPLATE = """Based on the Critic's findings, generate testable hypotheses.

Paper: {title}
Critic's weaknesses: {weaknesses}
Critic's missing experiments: {missing_experiments}
Scalability issues: {scalability_issues}"""


def hypothesis_node(state):
    # Skip if pipeline was paused upstream
    if state.get("pipeline_paused"):
        return {}
    # Skip if already computed (resume path)
    if state.get("hypothesis_output"):
        return {}

    logs   = list(state.get("agent_logs", []))
    critic = state.get("critic_output", {}) or {}

    logs.append({"agent": "Hypothesis", "message": "Analyzing critic findings...",     "status": "running"})
    logs.append({"agent": "Hypothesis", "message": "Generating testable hypotheses...","status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    key_update = {}
    try:
        logs.append({"agent": "Hypothesis", "message": "Mapping hypotheses to experiments...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":               title,
            "weaknesses":          json.dumps(critic.get("weaknesses",          [])),
            "missing_experiments": json.dumps(critic.get("missing_experiments", [])),
            "scalability_issues":  json.dumps(critic.get("scalability_issues",  [])),
        })
        result = parse_json_response(content)
        logs.append({"agent": "Hypothesis", "message": "✓ Hypotheses generated.","status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Hypothesis", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "hypothesis_output":  {},
            "agent_logs":         logs,
            "available_api_keys": e.available,
            "exhausted_api_keys": e.exhausted,
            "pipeline_paused":    True,
        }
    except Exception as e:
        result = {}
        logs.append({"agent": "Hypothesis", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"hypothesis_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

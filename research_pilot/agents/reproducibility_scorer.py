# agents/reproducibility_scorer.py — Node 8: Reproducibility Scorer
# Scores the paper 0-10 across 5 dimensions with specific reasons.

import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """You are a Reproducibility Analyst who evaluates research papers on
how easily another researcher could reproduce their results.

Score each dimension 0-10. Be specific — cite actual evidence from the paper.

Return ONLY valid JSON (no markdown fences):

{{
  "overall_score": 8.2,
  "verdict": "One sentence overall reproducibility verdict",
  "dimensions": {{
    "code_availability": {{
      "score": 9,
      "reason": "Specific evidence from paper"
    }},
    "dataset_access": {{
      "score": 8,
      "reason": "Specific evidence from paper"
    }},
    "compute_requirements": {{
      "score": 7,
      "reason": "Specific evidence from paper"
    }},
    "hyperparameter_clarity": {{
      "score": 9,
      "reason": "Specific evidence from paper"
    }},
    "ablation_completeness": {{
      "score": 8,
      "reason": "Specific evidence from paper"
    }}
  }},
  "strengths": [
    "Specific reproducibility strength with evidence"
  ],
  "weaknesses": [
    "Specific reproducibility weakness or barrier"
  ]
}}"""

HUMAN_TEMPLATE = """Score reproducibility for this paper.

Paper: {title}
Abstract: {abstract}
Methodology details (from Planner): {planner_output}
Critic's reproducibility risks: {repro_risks}
Content excerpt: {content}"""


def reproducibility_scorer_node(state):
    # Skip if pipeline was paused upstream
    if state.get("pipeline_paused"):
        return {}
    # Skip if already computed (resume path)
    if state.get("reproducibility_output"):
        return {}

    logs   = list(state.get("agent_logs", []))
    critic = state.get("critic_output", {}) or {}

    logs.append({"agent": "Repro Scorer", "message": "Evaluating code availability...", "status": "running"})
    logs.append({"agent": "Repro Scorer", "message": "Scoring dataset accessibility...","status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    key_update = {}
    try:
        logs.append({"agent": "Repro Scorer", "message": "Computing reproducibility score...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":          title,
            "abstract":       state.get("abstract",  "")[:2000],
            "planner_output": json.dumps(state.get("planner_output", {})),
            "repro_risks":    json.dumps(critic.get("reproducibility_risks", [])),
            "content":        state.get("raw_text",  "")[:5000],
        })
        result = parse_json_response(content)
        logs.append({"agent": "Repro Scorer", "message": "✓ Reproducibility scored.","status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Repro Scorer", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "reproducibility_output": {},
            "agent_logs":             logs,
            "available_api_keys":     e.available,
            "exhausted_api_keys":     e.exhausted,
            "pipeline_paused":        True,
        }
    except Exception as e:
        result = {}
        logs.append({"agent": "Repro Scorer", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"reproducibility_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

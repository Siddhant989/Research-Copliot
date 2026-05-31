# agents/synthesizer.py — Node 11: Synthesizer Agent
# Combines ALL agent outputs into the final structured report and generates the agent debate.

import json
from langchain_core.prompts import ChatPromptTemplate
from utils.llm_manager import invoke_with_fallback, AllKeysExhausted
from utils.helpers import parse_json_response


SYSTEM_PROMPT = """You are a Research Intelligence Synthesizer. You receive outputs from
9 specialist agents and combine them into a comprehensive, beginner-friendly report.

Return ONLY valid JSON (no markdown fences):

{{
  "plain_summary": {{
    "problem": "2-3 plain sentences: exact problem the paper solves",
    "why_it_matters": "2-3 sentences: real-world importance",
    "approach": "3-4 sentences: how the paper solves it, explain to a curious non-expert",
    "importance": "2-3 sentences: why this paper became important"
  }},
  "research_background": {{
    "narrative": "3-4 sentences: what existed before, plain English",
    "previous_approaches": [
      {{
        "method": "name",
        "description": "what it was",
        "limitation": "why it failed"
      }}
    ],
    "how_improved": "3-4 sentences: concrete improvements this paper made"
  }},
  "key_takeaways": [
    "Concise, insightful point — specific not vague"
  ],
  "methodology_breakdown": {{
    "overview": "2-3 sentences: the overall methodology",
    "datasets": [
      {{
        "name": "...",
        "size": "...",
        "task": "...",
        "public": true
      }}
    ],
    "optimizer": "optimizer name and key settings",
    "hardware": "GPUs/TPUs used",
    "training_time": "how long",
    "training_flow": [
      "Step 1: ...",
      "Step 2: ..."
    ],
    "evaluation_metrics": [
      "metric and what it measures"
    ]
  }},
  "architecture_info": {{
    "name": "Architecture name",
    "type": "Architecture type",
    "overview": "3-4 plain sentences describing the architecture",
    "components": [
      {{
        "name": "Component",
        "role": "one-sentence role",
        "explanation": "2-3 beginner sentences"
      }}
    ]
  }},
  "contributions": [
    {{
      "title": "Contribution name",
      "description": "Plain English explanation",
      "significance": "high"
    }}
  ],
  "future_ideas": [
    {{
      "idea": "Plain what-if description (2-3 sentences) — taken directly from the Hypothesis Agent's hypotheses",
      "why": "value proposition — use the hypothesis's expected_outcome as a guide",
      "difficulty": "beginner"
    }}
  ],
  "agent_debate": [
    {{
      "agent": "Research Agent",
      "message": "Specific claim or finding",
      "side": "pro"
    }},
    {{
      "agent": "Critic Agent",
      "message": "Specific counter-argument based on a real weakness the Critic identified",
      "side": "con"
    }},
    {{
      "agent": "Research Agent",
      "message": "Rebuttal with evidence from the paper",
      "side": "pro"
    }},
    {{
      "agent": "Critic Agent",
      "message": "Final critical point — name a specific missing experiment",
      "side": "con"
    }},
    {{
      "agent": "Planner Agent",
      "message": "Mediation: reference the Hypothesis Agent's priority hypothesis by ID and explain why testing it would resolve this debate",
      "side": "mediate"
    }}
  ]
}}

Rules:
- 6 key_takeaways
- 5 contributions with significance: high/medium/low
- 5 future_ideas — derive each one directly from the Hypothesis Agent's hypotheses list (use hypothesis, expected_outcome, difficulty fields). Do NOT invent new ideas.
- 5 agent_debate messages — Research vs Critic, mediated by Planner
- Planner's mediation message MUST name the Hypothesis Agent's priority_hypothesis ID (e.g. "H1") and reference what that hypothesis proposes
- Debate must feel like real researchers disagreeing — not generic statements
- Critic's weaknesses and missing experiments must come from the actual critic_output, not be invented
"""

HUMAN_TEMPLATE = """Synthesize all agent findings into the final report.

Paper: {title}
Abstract: {abstract}
Planner output: {planner}
Research output: {research}
Critic output: {critic}
Hypothesis output: {hypothesis}
Reproducibility output: {repro}

IMPORTANT — how to use the Hypothesis output:
1. The "hypotheses" list is your source for future_ideas. Map each hypothesis directly:
   - hypothesis.hypothesis → future_ideas.idea
   - hypothesis.expected_outcome → future_ideas.why
   - hypothesis.difficulty → future_ideas.difficulty
2. The "priority_hypothesis" field (e.g. "H1") is what the Planner Agent must name in the debate mediation message.
3. Do not invent future ideas from scratch — use what the Hypothesis Agent already worked out."""


def synthesizer_node(state):
    # Skip if pipeline was paused upstream
    if state.get("pipeline_paused"):
        return {}
    # Skip if already computed (resume path)
    if state.get("synthesizer_output"):
        return {}

    logs = list(state.get("agent_logs", []))
    logs.append({"agent": "Synthesizer", "message": "Combining all agent findings...", "status": "running"})
    logs.append({"agent": "Synthesizer", "message": "Writing plain-English summary...","status": "running"})

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human",  HUMAN_TEMPLATE),
    ])

    metadata = state.get("metadata", {})
    title = metadata.get("title", "") or state.get("paper_title", "")

    key_update = {}
    try:
        logs.append({"agent": "Synthesizer", "message": "Generating research intelligence report...","status": "running"})
        content, key_update = invoke_with_fallback(state, prompt, {
            "title":      title,
            "abstract":   state.get("abstract", "")[:2000],
            "planner":    json.dumps(state.get("planner_output",         {})),
            "research":   json.dumps(state.get("research_output",        {})),
            "critic":     json.dumps(state.get("critic_output",          {})),
            "hypothesis": json.dumps(state.get("hypothesis_output",      {})),
            "repro":      json.dumps(state.get("reproducibility_output", {})),
        })
        result = parse_json_response(content)
        logs.append({"agent": "Synthesizer", "message": "✓ Final report complete.","status": "done"})
    except AllKeysExhausted as e:
        logs.append({"agent": "Synthesizer", "message": "⚠ All API keys exhausted.","status": "error"})
        return {
            "synthesizer_output":  {},
            "agent_logs":          logs,
            "available_api_keys":  e.available,
            "exhausted_api_keys":  e.exhausted,
            "pipeline_paused":     True,
        }
    except Exception as e:
        result = {}
        logs.append({"agent": "Synthesizer", "message": f"⚠ Error: {str(e)[:60]}","status": "error"})

    return_data = {"synthesizer_output": result, "agent_logs": logs}
    if key_update:
        return_data["available_api_keys"] = key_update["available_api_keys"]
        return_data["exhausted_api_keys"] = key_update["exhausted_api_keys"]
    return return_data

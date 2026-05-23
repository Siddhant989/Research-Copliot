"""
app/agents/synthesizer.py — Synthesizer Agent

Role: The final agent in the pipeline. It reads ALL previous outputs and
      writes a coherent, structured research intelligence report.

This is what gets shown to the user as the main result.

Input state fields:  query, papers, critique, hypotheses, key_findings, repro_scores
Output state fields: synthesis
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


SYSTEM_PROMPT = """You are a senior research analyst writing an executive briefing.

You will receive:
  • The research topic
  • Key findings from recent papers
  • A critique of the literature's weaknesses
  • Testable hypotheses generated from those weaknesses
  • Reproducibility scores for each paper

Write a structured report with these exact sections:

## Overview
2-3 sentences summarising the state of research on this topic.

## Key Findings
Paste the key findings bullet points here (do not rewrite them).

## Literature Gaps & Critique
Paste the critique here (do not rewrite it).

## Recommended Next Steps
3 bullet points a researcher should do next, informed by the hypotheses.

## Reproducibility Summary
One sentence about the average reproducibility quality of the surveyed papers,
with the highest and lowest scored paper named.

Keep the tone professional and concise. Do not pad with filler sentences.
"""


def synthesizer_node(state: ResearchState) -> dict:
    """Synthesize all agent outputs into a final report."""
    print("[Synthesizer] Generating final report…")

    # Build a structured context block for the LLM
    repro_lines = "\n".join(
        f"  • {s['title'][:60]}… → {s['score']}/10 — {s['reasoning']}"
        for s in state.get("repro_scores", [])
    ) or "  No scores available."

    hypotheses_block = "\n".join(state.get("hypotheses", [])) or "None generated."
    findings_block   = "\n".join(state.get("key_findings", [])) or "None available."

    user_message = f"""Research Topic: {state["query"]}

KEY FINDINGS:
{findings_block}

CRITIQUE:
{state.get("critique", "N/A")}

HYPOTHESES:
{hypotheses_block}

REPRODUCIBILITY SCORES:
{repro_lines}
"""

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ])
        synthesis = response.content.strip()
    except Exception as e:
        synthesis = "Synthesis could not be generated."
        return {"synthesis": synthesis, "errors": state.get("errors", []) + [f"Synthesizer: {e}"]}

    print("[Synthesizer] Report complete.")
    return {"synthesis": synthesis}

"""
app/agents/synthesizer.py — Synthesizer Agent

Role: Pulls everything together into one clear, human-friendly report,
      plus per-paper structured analysis (methodology, assumptions, weaknesses).

Tone: Like a brilliant colleague who spent a week reading all the papers
and is now giving you the honest 5-minute version — what matters, what
doesn't, and what you should do next.

No academic jargon. Real sentences. Direct opinions.

Input state fields:  query, papers, critique, hypotheses, key_findings, repro_scores
Output state fields: synthesis, methodology, assumptions, weaknesses
"""

import json
import re

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


SYSTEM_PROMPT = """You are a brilliant research colleague giving someone
the honest, plain-English version of what's happening in a research area.

Write a report using these exact sections. Keep it real — like you're
explaining to a smart friend, not writing a formal paper.

## What's the big picture?
2-3 sentences. What is this research area trying to solve, and where does
it stand right now? Be direct and skip the history lesson.

## What we actually learned
Paste the key findings bullet points here exactly as given.
Don't rewrite them — just include them.

## What's broken or missing
Paste the critique bullet points here exactly as given.
Don't rewrite them — just include them.

## What someone should do next
3 concrete suggestions based on the research ideas provided.
Write each as: "Try this: [plain English description of the experiment]"
Give a one-sentence reason why it would matter.

## How trustworthy is this research?
One paragraph. Plain English verdict on whether these papers can be
reproduced — name the best and worst paper specifically.
Tell the reader what that means in practice (can they build on this work?).

Rules:
- No words like: "paradigm", "epistemological", "seminal", "aforementioned"
- No passive voice: say "researchers ignored X" not "X was ignored"
- Keep each section tight — cut anything that doesn't add value
"""


ANALYSIS_PROMPT = """You are a sharp research analyst reading a set of papers.
For each paper, extract three things in plain, readable English:

1. METHODOLOGY — how they actually did the research (approach, how they tested it, key steps)
2. ASSUMPTIONS — things they treated as true without proving (hidden assumptions)
3. WEAKNESSES — specific gaps or limitations in their approach

Output a single JSON object with exactly this shape:
{
  "methodology": [
    {
      "paper": "<exact paper title>",
      "approach": "<one sentence: what method/technique they used>",
      "how_tested": "<one sentence: how they measured success>",
      "steps": ["<key step 1>", "<key step 2>", "<key step 3>"]
    }
  ],
  "assumptions": [
    {
      "paper": "<exact paper title>",
      "assumptions": [
        "<assumption 1 — plain statement, no jargon>",
        "<assumption 2>",
        "<assumption 3>"
      ]
    }
  ],
  "weaknesses": [
    {
      "paper": "<exact paper title>",
      "weaknesses": [
        "<weakness 1 — specific, not vague>",
        "<weakness 2>",
        "<weakness 3>"
      ]
    }
  ]
}

Rules:
- Write for someone reading this research area for the first time
- Be specific: "only tested on English text" is good; "limited scope" is too vague
- Assumptions = things they take for granted (e.g. "more data always helps")
- Weaknesses = real gaps, missing experiments, or practical limits
- Keep every point to one sentence
- Output ONLY valid JSON, no markdown fences, no extra text
"""


def _strip_fences(raw: str) -> str:
    return re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()


def synthesizer_node(state: ResearchState) -> dict:
    print("[Synthesizer] Writing final report…")

    papers = state.get("papers", [])
    paper_text = "\n\n".join(
        f"Title: {p['title']}\nAbstract: {p.get('abstract', '')[:600]}"
        for p in papers
    )

    repro_lines = "\n".join(
        f"  • {s['title'][:55]}… → {s['score']}/10 — {s['reasoning']}"
        for s in state.get("repro_scores", [])
    ) or "  No scores available."

    hypotheses_block = "\n".join(state.get("hypotheses", [])) or "None generated."
    findings_block   = "\n".join(state.get("key_findings", [])) or "None available."

    # ── Call 1: narrative synthesis ───────────────────────────────────────────
    user_message = f"""Research topic: {state["query"]}

KEY FINDINGS (paste these into the report as-is):
{findings_block}

CRITIQUE (paste these into the report as-is):
{state.get("critique", "N/A")}

RESEARCH IDEAS TO DRAW FROM:
{hypotheses_block}

REPRODUCIBILITY SCORES:
{repro_lines}
"""

    try:
        resp1     = llm.invoke([SystemMessage(content=SYSTEM_PROMPT),
                                HumanMessage(content=user_message)])
        synthesis = resp1.content.strip()
    except Exception as e:
        synthesis = "Could not generate the final report."
        return {
            "synthesis":   synthesis,
            "methodology": [], "assumptions": [], "weaknesses": [],
            "errors": state.get("errors", []) + [f"Synthesizer: {e}"],
        }

    # ── Call 2: structured per-paper analysis (methodology/assumptions/weaknesses)
    print("[Synthesizer] Extracting methodology, assumptions, weaknesses…")
    try:
        resp2   = llm.invoke([
            SystemMessage(content=ANALYSIS_PROMPT),
            HumanMessage(content=f"Topic: {state['query']}\n\nPapers:\n{paper_text}"),
        ])
        parsed  = json.loads(_strip_fences(resp2.content))
        methodology = parsed.get("methodology", [])
        assumptions = parsed.get("assumptions", [])
        weaknesses  = parsed.get("weaknesses",  [])
    except Exception as e:
        methodology = [{"paper": p["title"], "approach": "Could not extract.",
                        "how_tested": "N/A", "steps": []} for p in papers]
        assumptions = [{"paper": p["title"], "assumptions": ["Could not extract."]} for p in papers]
        weaknesses  = [{"paper": p["title"], "weaknesses":  ["Could not extract."]} for p in papers]
        print(f"[Synthesizer] Analysis extraction error: {e}")

    print("[Synthesizer] Done.")
    return {
        "synthesis":   synthesis,
        "methodology": methodology,
        "assumptions": assumptions,
        "weaknesses":  weaknesses,
    }

"""
app/agents/tech_analyzer.py — Tech Analyzer Agent

What it does (plain English):
  Reads the papers and tells you two things:
    1. WHAT they built — models, architectures, key numbers, datasets, compute
    2. HOW to try it yourself — a short, runnable Python snippet that
       demonstrates the core idea of the most interesting paper

Why this is useful:
  - You can see at a glance what tools/hardware you'd need to reproduce each paper
  - The code snippet lets viewers go from "interesting paper" to
    "I can run something related to this" in 5 minutes

Output:
  model_profiles  — list of per-paper tech profiles
  code_snippet    — a 20-40 line Python snippet with comments

Input state fields:  papers, query
Output state fields: model_profiles, code_snippet
"""

import json
import re

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm


# ── Prompt 1: extract model/tech profile per paper ────────────────────────────

PROFILE_PROMPT = """You are a technical research analyst.

For each paper, extract the key technical details in plain English.
Output a JSON array — one object per paper — with this exact shape:

[
  {
    "paper": "<exact paper title>",
    "architecture": "<what type of model/system — e.g. Transformer, CNN, GAN>",
    "key_components": ["<component 1>", "<component 2>", "<component 3>"],
    "parameters": "<model size — e.g. 110M params, 7B params, or N/A>",
    "training_data": "<what dataset(s) were used — be specific>",
    "compute": "<hardware and time — e.g. 8x A100, 3 days — or N/A if not mentioned>",
    "framework": "<PyTorch / TensorFlow / JAX / other>"
  }
]

Rules:
- If a detail isn't mentioned in the abstract, write "Not specified"
- Keep each field short — one line max
- Output ONLY valid JSON, no markdown fences, no extra text
"""


# ── Prompt 2: generate a runnable code snippet ────────────────────────────────

SNIPPET_PROMPT = """You are a practical ML engineer who loves writing
clean, readable demo code.

Given a research topic and papers, write a short Python snippet (20-35 lines)
that demonstrates the CORE IDEA of this research — something a person
could copy, paste, and run in under 5 minutes.

Rules:
- Use only standard libraries OR PyTorch/NumPy (assume they're installed)
- Add a comment at the top: # What this shows: [one sentence]
- Add short inline comments explaining each key step
- Keep it simple enough that a junior engineer understands it
- Make it actually runnable — no placeholder functions or missing imports
- If the concept is complex, demonstrate a scaled-down version

Output ONLY the Python code. No explanation, no markdown fences.
"""


def _strip_fences(raw: str) -> str:
    return re.sub(r"```(?:json|python)?", "", raw).strip().rstrip("`").strip()


def tech_analyzer_node(state: ResearchState) -> dict:
    papers = state.get("papers", [])
    if not papers:
        return {
            "model_profiles": [],
            "code_snippet":   "",
            "errors": state.get("errors", []) + ["TechAnalyzer: skipped — no papers."],
        }

    print(f"[TechAnalyzer] Profiling {len(papers)} papers…")

    # Build a compact paper list for both prompts
    paper_text = "\n\n".join(
        f"Title: {p['title']}\n"
        f"Published: {p.get('published', 'N/A')}\n"
        f"Abstract: {p['abstract'][:500]}"
        for p in papers
    )

    # ── Step 1: model profiles ─────────────────────────────────────────────
    try:
        resp1         = llm.invoke([
            SystemMessage(content=PROFILE_PROMPT),
            HumanMessage(content=f"Topic: {state['query']}\n\nPapers:\n{paper_text}"),
        ])
        model_profiles = json.loads(_strip_fences(resp1.content))
    except Exception as e:
        model_profiles = [{"paper": p["title"], "architecture": "Could not extract",
                           "key_components": [], "parameters": "N/A",
                           "training_data": "N/A", "compute": "N/A", "framework": "N/A"}
                          for p in papers]
        print(f"[TechAnalyzer] Profile extraction error: {e}")

    # ── Step 2: runnable code snippet ─────────────────────────────────────
    try:
        resp2        = llm.invoke([
            SystemMessage(content=SNIPPET_PROMPT),
            HumanMessage(content=f"Topic: {state['query']}\n\nPapers:\n{paper_text}"),
        ])
        code_snippet = _strip_fences(resp2.content)
    except Exception as e:
        code_snippet = f"# Could not generate code snippet\n# Error: {e}"
        print(f"[TechAnalyzer] Snippet generation error: {e}")

    print(f"[TechAnalyzer] Done — {len(model_profiles)} profiles, "
          f"{len(code_snippet.splitlines())} lines of code.")
    return {"model_profiles": model_profiles, "code_snippet": code_snippet}

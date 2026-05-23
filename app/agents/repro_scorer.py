"""
app/agents/repro_scorer.py — Reproducibility Scorer

Works in two modes:
  • arXiv mode  — only an abstract is available (Phase 2)
  • PDF mode    — full paper text + pre-detected code/dataset signals (Phase 3)

Scoring rubric (0–10):
  +2  Code / repository mentioned or found
  +2  Named public dataset used or found
  +2  Detailed methodology or hyperparameters described
  +2  Multiple baselines compared
  +1  Ablation study mentioned
  +1  Standard benchmarks used

Input state fields:  papers
Output state fields: repro_scores  (list of {title, score, reasoning, signals})
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import ResearchState
from app.agents.llm import llm
import json
import re


SYSTEM_PROMPT = """You are a reproducibility auditor for machine learning and AI papers.

For each paper provided, output a JSON array where each element is:
{
  "title": "<exact paper title>",
  "score": <integer 0-10>,
  "reasoning": "<one sentence explaining the score>"
}

Score based on these signals present in the text:
  • Code / repository mentioned or linked → +2
  • Named public dataset used or available → +2
  • Detailed methodology or hyperparameters described → +2
  • Multiple baselines compared → +2
  • Ablation study mentioned → +1
  • Standard benchmarks used → +1

You may receive either a short abstract (arXiv papers) or a longer excerpt
from a full paper (PDF uploads) — use whatever is provided.
Pre-detected signals (code_mentions, dataset_mentions) are already confirmed
present in the paper; count them as found even if not in the text excerpt.

Output ONLY valid JSON — no markdown fences, no extra text.
"""


def _build_prompt(papers: list) -> str:
    """
    Build the scoring prompt.  For PDF papers, include the full_text excerpt
    and any pre-detected signals.  For arXiv papers, use the abstract.
    """
    entries = []
    for p in papers:
        is_pdf = p.get("source") == "pdf_upload"

        if is_pdf:
            # Use up to 1500 chars of full text for richer signal detection
            text_excerpt = p.get("full_text", p.get("abstract", ""))[:1500]
            code_sigs    = p.get("code_mentions", [])
            data_sigs    = p.get("dataset_mentions", [])

            entry = (
                f"Title: {p['title']}\n"
                f"Source: full PDF ({p.get('page_count', '?')} pages, "
                f"~{p.get('word_count', '?')} words)\n"
            )
            if code_sigs:
                entry += f"Pre-detected code signals: {', '.join(code_sigs[:5])}\n"
            if data_sigs:
                entry += f"Pre-detected dataset signals: {', '.join(data_sigs[:5])}\n"
            entry += f"Text excerpt:\n{text_excerpt}"
        else:
            entry = (
                f"Title: {p['title']}\n"
                f"Categories: {', '.join(p.get('categories', []))}\n"
                f"Abstract: {p['abstract'][:600]}"
            )
        entries.append(entry)

    return "\n\n---\n\n".join(entries)


def repro_scorer_node(state: ResearchState) -> dict:
    """Score each paper for reproducibility."""
    papers = state.get("papers", [])

    if not papers:
        return {
            "repro_scores": [],
            "errors": state.get("errors", []) + ["ReproScorer: skipped — no papers."],
        }

    mode = "PDF" if papers[0].get("source") == "pdf_upload" else "arXiv"
    print(f"[ReproScorer] Scoring {len(papers)} papers in {mode} mode…")

    try:
        response = llm.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=_build_prompt(papers)),
        ])
        raw = response.content.strip()

        # Strip markdown fences if the model added them anyway
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

        scores = json.loads(raw)

        # Attach pre-detected signals to each score entry for the frontend
        title_to_paper = {p["title"]: p for p in papers}
        for s in scores:
            matched = title_to_paper.get(s.get("title"), {})
            s["code_mentions"]    = matched.get("code_mentions", [])
            s["dataset_mentions"] = matched.get("dataset_mentions", [])

    except json.JSONDecodeError:
        scores = [
            {
                "title": p["title"], "score": 5,
                "reasoning": "Could not parse LLM score output.",
                "code_mentions": p.get("code_mentions", []),
                "dataset_mentions": p.get("dataset_mentions", []),
            }
            for p in papers
        ]
        return {
            "repro_scores": scores,
            "errors": state.get("errors", []) + ["ReproScorer: JSON parse failed, used fallback scores."],
        }
    except Exception as e:
        scores = [
            {"title": p["title"], "score": 5, "reasoning": "Scoring error.",
             "code_mentions": [], "dataset_mentions": []}
            for p in papers
        ]
        return {"repro_scores": scores, "errors": state.get("errors", []) + [f"ReproScorer: {e}"]}

    print(f"[ReproScorer] Done. Scores: {[s['score'] for s in scores]}")
    return {"repro_scores": scores}

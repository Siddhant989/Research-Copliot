import os
import json
import time
import shutil
import pandas as pd
import streamlit as st
from pathlib import Path
from demo.attention_demo import ATTENTION_DEMO

# Cache directory for extracted assets (figures, tables, JSON cache)
CACHE_DIR = Path("extracted_assets/cache")

# Page config — must be the first Streamlit call
st.set_page_config(
    page_title="ResearchPilot AI",
    page_icon="🔬",
    layout="wide",
)


# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════════════════

def render_sidebar(state: dict) -> None:
    meta  = state.get("metadata", {}) or {}
    repro = state.get("reproducibility_output", {}) or {}

    with st.sidebar:
        st.header("🔬 ResearchPilot AI")
        st.caption("Multi-Agent Research Analysis")
        st.divider()

        if meta.get("title"):
            st.subheader("📄 Current Paper")
            st.write(f"**{meta.get('title', '')[:80]}**")

            authors = meta.get("authors", [])
            if authors:
                st.caption(", ".join(authors[:3]) + ("…" if len(authors) > 3 else ""))

            if meta.get("year"):
                st.caption(f"Published: {meta['year']}")

            if meta.get("url"):
                st.link_button("Open on arXiv ↗", meta["url"])

            if repro.get("overall_score"):
                st.divider()
                st.metric("Reproducibility Score", f"{repro['overall_score']} / 10")

        st.divider()
        st.subheader("🤖 The 10 Research Agents")
        agents_info = [
            ("📄", "Paper Fetcher",
             "Searches arXiv and downloads the paper"),
            ("📑", "PDF Extractor",
             "Reads the PDF and pulls out text, sections, and figures"),
            ("🧭", "Planner",
             "Maps out the research objective and breaks down the methodology"),
            ("📚", "Research Agent",
             "Reviews prior work and related approaches in the field"),
            ("🔬", "Critic Agent",
             "Finds weaknesses, gaps, and risky assumptions in the paper"),
            ("💡", "Hypothesis Agent",
             "Proposes specific, testable follow-up research ideas"),
            ("📊", "Repro Scorer",
             "Rates how easy it would be to reproduce the results"),
            ("💻", "Code Agent",
             "Writes beginner-friendly implementation code for the core idea"),
            ("🔍", "Evidence Tracker",
             "Traces every claim back to a direct quote from the paper"),
            ("✨", "Synthesizer",
             "Combines all findings into the final structured report"),
        ]
        for emoji, name, desc in agents_info:
            st.markdown(f"**{emoji} {name}**")
            st.caption(desc)


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 1 — Overview
# ═══════════════════════════════════════════════════════════════════════════════

def render_overview(state: dict) -> None:
    synth     = state.get("synthesizer_output", {}) or {}
    meta      = state.get("metadata", {}) or {}
    plain     = synth.get("plain_summary", {})
    arch      = synth.get("architecture_info", {})
    contribs  = synth.get("contributions", [])
    takeaways = synth.get("key_takeaways", [])

    title   = meta.get("title", state.get("paper_title", "Research Paper"))
    authors = ", ".join(meta.get("authors", [])[:4])
    if len(meta.get("authors", [])) > 4:
        authors += " et al."
    year = meta.get("year", "")

    st.title(f"📄 {title}")
    st.caption(f"By {authors} · {year} · Analysed by 10 AI Research Agents")
    st.divider()

    # Plain English summary
    if plain:
        st.subheader("What Is This Paper About?")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔍 The Problem**")
            st.info(plain.get("problem", ""))
            st.markdown("**⚙️ How They Solved It**")
            st.info(plain.get("approach", ""))
        with col2:
            st.markdown("**🌍 Why It Matters**")
            st.info(plain.get("why_it_matters", ""))
            st.markdown("**⭐ Why This Paper Is Important**")
            st.info(plain.get("importance", ""))

    # Key takeaways
    if takeaways:
        st.divider()
        st.subheader("⚡ Key Takeaways")
        for i, point in enumerate(takeaways, 1):
            st.markdown(f"**{i}.** {point}")

    # Contributions
    if contribs:
        st.divider()
        st.subheader("🏆 Key Contributions")
        for c in contribs:
            sig = c.get("significance", "medium")
            label = "🔴 High Impact" if sig == "high" else "🟡 Medium Impact" if sig == "medium" else "🟢 Lower Impact"
            with st.expander(f"{label} — {c.get('title', '')}"):
                st.write(c.get("description", ""))

    # Architecture overview
    if arch:
        st.divider()
        st.subheader("🏗️ Architecture Overview")
        st.write(f"**Model:** {arch.get('name', '')} ({arch.get('type', '')})")
        st.write(arch.get("overview", ""))

        components = arch.get("components", [])
        if components:
            st.markdown("**Building Blocks:**")
            cols = st.columns(min(len(components), 3))
            for i, comp in enumerate(components):
                with cols[i % 3]:
                    with st.expander(f"🔧 {comp.get('name', '')}"):
                        st.caption(comp.get("role", ""))
                        st.write(comp.get("explanation", ""))


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 2 — Deep Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def render_deep_analysis(state: dict) -> None:
    synth    = state.get("synthesizer_output", {}) or {}
    bg       = synth.get("research_background", {})
    method   = synth.get("methodology_breakdown", {})
    evidence = state.get("evidence_tracker_output", []) or []

    # Research background
    if bg:
        st.subheader("📚 Research Background")
        st.write(bg.get("narrative", ""))

        prev = bg.get("previous_approaches", [])
        if prev:
            st.markdown("### What Was Tried Before (and Why It Wasn't Enough)")
            st.write("Researchers had tried several approaches before this paper. Here's a plain-English breakdown of each one:")
            for p in prev:
                with st.expander(f"❌ Approach: {p.get('method', '')}"):
                    st.markdown("**What it was:**")
                    st.write(p.get("description", ""))
                    st.markdown("**Why it didn't fully work:**")
                    st.warning(p.get("limitation", ""))

        if bg.get("how_improved"):
            st.markdown("### ✅ How This Paper Fixed It")
            st.success(bg.get("how_improved", ""))

    # Methodology breakdown
    if method:
        st.divider()
        st.subheader("⚙️ How They Built and Trained It")
        st.write(method.get("overview", ""))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Optimizer Used", method.get("optimizer", "N/A"))
        with col2:
            st.metric("Hardware", method.get("hardware", "N/A"))
        with col3:
            st.metric("Training Time", method.get("training_time", "N/A"))

        flow = method.get("training_flow", [])
        if flow:
            st.markdown("**Step-by-step training process:**")
            for i, step in enumerate(flow, 1):
                st.markdown(f"{i}. {step}")

        datasets = method.get("datasets", [])
        if datasets:
            st.markdown("**Datasets Used:**")
            dcols = st.columns(len(datasets))
            for i, ds in enumerate(datasets):
                with dcols[i]:
                    pub = "✅ Publicly available" if ds.get("public") else "🔒 Private"
                    st.info(
                        f"**{ds.get('name', '')}**\n\n"
                        f"Size: {ds.get('size', '')}\n\n"
                        f"Used for: {ds.get('task', '')}\n\n"
                        f"{pub}"
                    )

    # Evidence & Citations
    if evidence:
        st.divider()
        st.subheader("🔍 Evidence & Citations")
        st.write("These are the main claims made by our AI agents, with direct quotes from the paper to back them up. Click any claim to see where it comes from.")
        for ev in evidence:
            with st.expander(f"📌 {ev.get('claim', '')}"):
                st.caption(
                    f"Source: {ev.get('agent_source', '')} agent  ·  "
                    f"Section: {ev.get('section', '')}  ·  "
                    f"Page {ev.get('page_number', '')}"
                )
                st.markdown("**Direct quote from the paper:**")
                st.info(f'"{ev.get("supporting_quote", "")}"')


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 3 — Critique & Debate
# ═══════════════════════════════════════════════════════════════════════════════

def render_critique(state: dict) -> None:
    critic = state.get("critic_output",      {}) or {}
    synth  = state.get("synthesizer_output", {}) or {}
    debate = synth.get("agent_debate",       []) or []

    # Weaknesses
    weaknesses = critic.get("weaknesses", [])
    if weaknesses:
        st.subheader("⚠️ Problems Found in the Paper")
        for w in weaknesses:
            sev = w.get("severity", "medium")
            text = f"**{w.get('issue', '')}** — {w.get('impact', '')}"
            if sev == "high":
                st.error(text)
            elif sev == "medium":
                st.warning(text)
            else:
                st.info(text)

    # Hidden assumptions
    assumptions = critic.get("assumptions", [])
    if assumptions:
        st.divider()
        st.subheader("🔮 Hidden Assumptions")
        st.write("Things the paper assumes are true without fully proving them:")
        for a in assumptions:
            with st.expander(f"🤔 {a.get('assumption', '')}"):
                st.write(f"**Risk if this is wrong:** {a.get('risk', '')}")

    # Missing experiments
    missing = critic.get("missing_experiments", [])
    if missing:
        st.divider()
        st.subheader("🔭 Experiments That Should Have Been Done")
        for exp in missing:
            if isinstance(exp, dict):
                st.markdown(f"- **{exp.get('experiment', '')}** — {exp.get('reason', '')}")
            else:
                st.markdown(f"- {exp}")

    # Agent debate
    if debate:
        st.divider()
        st.subheader("🎭 AI Agent Debate: Research Agent vs Critic Agent")
        st.caption("Our AI agents debate the strengths and weaknesses of the paper.")
        for msg in debate:
            side  = msg.get("side", "pro")
            agent = msg.get("agent", "")
            text  = msg.get("message", "")
            if side == "pro":
                st.success(f"**{agent}:** {text}")
            elif side == "con":
                st.error(f"**{agent}:** {text}")
            else:
                st.info(f"**{agent} (Mediator):** {text}")

    # Fairness note
    fairness = critic.get("fairness_note", "")
    if fairness:
        st.divider()
        st.subheader("⚖️ One Thing the Critic Admits Is Good")
        st.write(fairness)


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 4 — Reproducibility
# ═══════════════════════════════════════════════════════════════════════════════

def render_reproducibility(state: dict) -> None:
    repro = state.get("reproducibility_output", {}) or {}
    if not repro:
        st.info("Reproducibility analysis not available yet.")
        return

    overall = repro.get("overall_score", 0)
    verdict = repro.get("verdict", "")
    dims    = repro.get("dimensions", {})

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Overall Score", f"{overall} / 10")
    with col2:
        st.write("**Verdict:**")
        st.write(verdict)

    dim_labels = {
        "code_availability":      "Code Availability",
        "dataset_access":         "Dataset Access",
        "compute_requirements":   "Compute Requirements",
        "hyperparameter_clarity": "Hyperparameter Clarity",
        "ablation_completeness":  "Ablation Study Completeness",
    }
    if dims:
        st.divider()
        st.subheader("Breakdown by Category")
        for key, label in dim_labels.items():
            d      = dims.get(key, {})
            score  = d.get("score", 0)
            reason = d.get("reason", "")
            st.markdown(f"**{label}:** {score}/10")
            st.progress(score / 10)
            st.caption(reason)

    col1, col2 = st.columns(2)
    with col1:
        strengths = repro.get("strengths", [])
        if strengths:
            st.subheader("✅ What Makes It Easy to Reproduce")
            for s in strengths:
                st.success(f"✓ {s}")
    with col2:
        weak = repro.get("weaknesses", [])
        if weak:
            st.subheader("❌ What Makes It Hard to Reproduce")
            for w in weak:
                st.error(f"✗ {w}")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 5 — Try It Yourself (Code)
# ═══════════════════════════════════════════════════════════════════════════════

def render_code(state: dict) -> None:
    code = state.get("code_output", {}) or {}
    if not code:
        st.info("Code implementation not available yet.")
        return

    desc    = code.get("description", "")
    prereqs = code.get("prerequisites", [])
    steps   = code.get("steps", [])
    output  = code.get("expected_output", "")

    st.subheader("💻 Try It Yourself")
    st.write(desc)
    if prereqs:
        st.caption(f"You'll need: {', '.join(prereqs)}")

    for i, step in enumerate(steps, 1):
        with st.expander(f"Step {i}: {step.get('title', '')}", expanded=(i == 1)):
            explanation = step.get("explanation", "")
            code_text   = step.get("code", "")
            if explanation:
                st.write(explanation)
            if code_text:
                st.code(code_text, language="python")

    if output:
        st.subheader("📤 What You Should See When You Run It")
        st.code(output, language="text")


# ═══════════════════════════════════════════════════════════════════════════════
# Tab 6 — Research Ideas
# ═══════════════════════════════════════════════════════════════════════════════

def render_ideas(state: dict) -> None:
    hypo      = state.get("hypothesis_output",  {}) or {}
    synth     = state.get("synthesizer_output", {}) or {}
    ideas     = synth.get("future_ideas",    [])
    hypos     = hypo.get("hypotheses",       [])
    priority  = hypo.get("priority_hypothesis", "")
    rationale = hypo.get("rationale", "")

    if rationale:
        st.info(f"**🎯 Most Important Idea to Try First:** {rationale}")

    if hypos:
        st.subheader("🧪 Research Questions You Could Explore")
        st.write(
            "These are specific, testable research ideas based on the weaknesses our Critic Agent found. "
            "Each one could be a small research project or university assignment on its own."
        )
        for h in hypos:
            is_priority  = (h.get("id") == priority)
            diff         = h.get("difficulty", "beginner")
            etime        = h.get("estimated_time", "")
            diff_emoji   = "🟢" if diff == "beginner" else "🟡" if diff == "intermediate" else "🔴"
            title_prefix = "⭐ PRIORITY — " if is_priority else ""
            label        = f"{title_prefix}{diff_emoji} {h.get('hypothesis', '')[:90]}…"

            with st.expander(label, expanded=is_priority):
                st.write(h.get("hypothesis", ""))
                st.markdown(f"**Difficulty:** {diff.capitalize()} &nbsp;·&nbsp; **Estimated time:** {etime}")
                st.markdown(f"**This addresses the weakness:** *{h.get('weakness_addressed', '')}*")
                st.markdown("---")
                st.markdown("**How to test it (step by step):**")
                st.write(h.get("methodology", ""))
                st.markdown("**What success looks like:**")
                st.write(h.get("expected_outcome", ""))

    if ideas:
        st.divider()
        st.subheader("💡 Bigger Future Research Directions")
        st.write("These are larger ideas for where this field could go next:")
        for idea in ideas:
            diff       = idea.get("difficulty", "beginner")
            diff_emoji = "🟢" if diff == "beginner" else "🟡" if diff == "intermediate" else "🔴"
            with st.expander(f"{diff_emoji} {idea.get('idea', '')[:90]}…"):
                st.write(idea.get("idea", ""))
                st.caption(f"Why this is worth exploring: {idea.get('why', '')}")


# ═══════════════════════════════════════════════════════════════════════════════
# Additional Tools — RAG helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _ensure_rag_ready(state: dict) -> bool:
    """
    Build the ChromaDB index if not already done. Returns True when ready.
    Uses Gemini Vision API for real image-based explanations.
    API keys are rotated on quota errors via gemini_direct_call.
    Results are cached per paper — second call is instant.
    """
    if st.session_state.rag_ready:
        return True

    pdf_path = state.get("pdf_path") or ""
    if not pdf_path or not os.path.exists(pdf_path):
        return False

    with st.spinner("Extracting and explaining figures and tables from PDF…"):
        from utils.figure_explainer import get_or_create_assets
        from rag.embedder           import reset_and_build

        # Use arxiv_id as cache key when available
        arxiv_id = (state.get("metadata") or {}).get("arxiv_id", "")
        paper_id = arxiv_id if arxiv_id else None

        try:
            assets = get_or_create_assets(pdf_path, paper_id=paper_id)
        except Exception as e:
            st.error(f"Could not extract figures and tables: {e}")
            return False

        reset_and_build(assets)
        st.session_state.rag_assets = assets
        st.session_state.rag_ready  = True

    return True


def render_figures_tables(state: dict) -> None:
    """
    Show extracted figures and tables with AI explanations.
    For demo mode, rag_ready + rag_assets are set by the demo button handler.
    For live mode, _ensure_rag_ready() runs extraction on first click (cached after).
    """
    st.subheader("🖼️ Extracted Figures & Tables")

    if state is None:
        st.info("Please analyse a paper first.")
        return

    ready = _ensure_rag_ready(state)
    if not ready:
        st.info("No PDF available. Run a live analysis to extract figures and tables.")
        return

    assets  = st.session_state.rag_assets
    figures = assets.get("figures", [])
    tables  = assets.get("tables",  [])

    if not figures and not tables:
        st.warning("No figures or tables were found in this paper's PDF.")
        return

    if figures:
        st.markdown("#### Figures")
        for fig in figures:
            img_path = fig.get("image_path") or ""
            caption  = fig.get("caption",     "")
            page     = fig.get("page_number", "?")
            expl     = fig.get("explanation", "")

            col_img, col_txt = st.columns([1, 1], gap="large")
            with col_img:
                if img_path and os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                st.caption(caption)
            with col_txt:
                if expl:
                    st.markdown("**AI Explanation:**")
                    st.write(expl)
                st.caption(f"Page {page}")

    if tables:
        st.markdown("#### Tables")
        for tbl in tables:
            caption    = tbl.get("caption",    "")
            page       = tbl.get("page_number") or tbl.get("page", "?")
            section    = tbl.get("section_name") or tbl.get("label", "")
            table_data = tbl.get("table_data",  [])
            expl       = tbl.get("explanation", "")

            st.markdown(f"**{caption}**")
            st.caption(f"Page {page} · {section}")

            if table_data:
                try:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True)
                except Exception:
                    pass

            if expl:
                st.markdown("**AI Explanation:**")
                st.write(expl)
            st.divider()


def render_ask_paper(state: dict) -> None:
    """RAG-powered Q&A about the paper."""
    st.subheader("💬 Ask The Paper")

    if state is None:
        st.info("Please analyse a paper first.")
        return

    title = state.get("metadata", {}).get("title", state.get("paper_title", ""))

    ready = _ensure_rag_ready(state)
    if not ready:
        st.info("No PDF available for Q&A. Run a live analysis to enable this feature.")
        return

    st.write(
        f"Ask any question about **{title}**. "
        "The system finds the most relevant sections and uses AI to give you an answer."
    )

    q_col, btn_col = st.columns([5, 1])
    with q_col:
        user_q = st.text_input(
            label="qa_input_label",
            placeholder='e.g. "How many attention heads?" or "What datasets were used?"',
            label_visibility="collapsed",
            key="qa_text_input",
        )
    with btn_col:
        ask_btn = st.button("Ask →", type="primary", use_container_width=True, key="qa_ask_btn")

    if ask_btn and user_q.strip():
        with st.spinner("Searching the paper and generating an answer…"):
            from rag.retriever import retrieve
            from rag.explainer import answer_question
            chunks = retrieve(user_q.strip())
            # Pass state so answer_question can use invoke_with_fallback in live mode
            answer, key_updates = answer_question(
                question=user_q.strip(),
                chunks=chunks,
                title=title,
                state=state,
            )
            # Propagate updated key lists back to live-pipeline state
            if key_updates and st.session_state.result and not st.session_state.demo_mode:
                st.session_state.result["available_api_keys"] = key_updates.get(
                    "available_api_keys", []
                )
                st.session_state.result["exhausted_api_keys"] = key_updates.get(
                    "exhausted_api_keys", []
                )
        st.session_state.qa_history.insert(0, {
            "question": user_q.strip(),
            "answer":   answer,
            "chunks":   chunks,
        })

    for item in st.session_state.qa_history:
        q      = item["question"]
        ans    = item["answer"]
        chunks = item["chunks"]

        st.markdown(f"**❓ {q}**")
        st.info(ans)

        fig_chunks = [c for c in chunks if c["metadata"].get("type") == "figure"]
        tbl_chunks = [c for c in chunks if c["metadata"].get("type") == "table"]

        for fc in fig_chunks[:2]:
            meta     = fc["metadata"]
            img_path = meta.get("image_path", "")
            caption  = meta.get("caption",     "")
            page     = meta.get("page_number", "?")
            section  = meta.get("section_name","")
            vc1, vc2 = st.columns([1, 2], gap="medium")
            with vc1:
                if img_path and os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                st.caption(caption)
            with vc2:
                st.caption(f"Page {page} · {section}")

        for tc in tbl_chunks[:2]:
            meta       = tc["metadata"]
            caption    = meta.get("caption",    "")
            page       = meta.get("page_number","?")
            section    = meta.get("section_name","")
            table_json = meta.get("table_data", "[]")
            st.caption(f"{caption} · Page {page} · {section}")
            try:
                df = pd.DataFrame(json.loads(table_json))
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
            except Exception:
                pass

        if chunks:
            with st.expander("View source evidence", expanded=False):
                for chunk in chunks[:5]:
                    meta    = chunk["metadata"]
                    ctype   = meta.get("type",         "").upper()
                    page    = meta.get("page_number",  "?")
                    section = meta.get("section_name", "")
                    quote   = chunk.get("document",    "")[:220]
                    st.caption(f"{ctype} · Page {page} · {section}")
                    st.markdown(f'*"{quote}…"*')
                    st.divider()

        st.divider()


# ═══════════════════════════════════════════════════════════════════════════════
# Key-exhausted resume dialog
# ═══════════════════════════════════════════════════════════════════════════════

def _render_key_exhausted_dialog() -> None:
    """Shown when all API keys are exhausted mid-pipeline."""
    exhausted = (st.session_state.paused_state or {}).get("exhausted_api_keys", [])
    n_ex      = len(exhausted)

    st.error(
        f"🔑 **All API Keys Exhausted** — {n_ex} key{'s' if n_ex != 1 else ''} "
        "hit the quota limit. The pipeline paused and will **resume from where it stopped** "
        "once you provide a fresh key — no restart needed."
    )

    with st.form("rp_new_key_form", clear_on_submit=True):
        new_key = st.text_input(
            "Paste your new Google AI / Gemini API key:",
            type="password",
            placeholder="AIza…",
        )
        submitted = st.form_submit_button("✅ Validate & Resume", type="primary", use_container_width=True)

    if submitted and new_key.strip():
        from utils.llm_manager import validate_api_key, save_api_key_to_env
        from graph.workflow    import resume_pipeline

        with st.spinner("Validating key…"):
            valid, msg = validate_api_key(new_key)

        if not valid:
            st.error(msg)
            return

        st.success(msg)
        key_name = save_api_key_to_env(new_key)
        st.info(f"Key saved as `{key_name}`.")

        with st.status("▶ Resuming pipeline from where it paused…", expanded=True) as status:
            try:
                run_result = resume_pipeline(st.session_state.paused_state, new_key)
                st.session_state.result          = run_result["state"]
                st.session_state.pipeline_paused = run_result["paused"]
                st.session_state.paused_state    = run_result["state"] if run_result["paused"] else None
                st.session_state.rag_ready       = False
                st.session_state.rag_assets      = {}

                if run_result["paused"]:
                    status.update(label="⚠ Keys exhausted again — please provide another key.", state="error")
                else:
                    status.update(label="✅ Pipeline complete!", state="complete")
                st.rerun()
            except Exception as exc:
                status.update(label=f"❌ Resume error: {exc}", state="error")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Session state init
    defaults = {
        "result":          None,
        "demo_mode":       False,
        "pipeline_paused": False,
        "paused_state":    None,
        "rag_ready":       False,
        "rag_assets":      {},
        "show_figures":    False,
        "show_qa":         False,
        "qa_history":      [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Header input bar ──────────────────────────────────────────────────────
    st.markdown("##### 🔬 ResearchPilot AI — Multi-Agent Paper Analysis")
    st.divider()

    col_input, col_btn, col_demo = st.columns([5, 1, 1])
    with col_input:
        query = st.text_input(
            label="paper_input",
            placeholder='Paper title or arXiv URL  (e.g. "Attention Is All You Need"  or  https://arxiv.org/abs/1706.03762)',
            label_visibility="collapsed",
        )
    with col_btn:
        analyse_btn = st.button("🔍 Analyse", use_container_width=True, type="primary")
    with col_demo:
        demo_btn = st.button("⚡ Demo", use_container_width=True)

    # ── Button handlers ───────────────────────────────────────────────────────
    if demo_btn:
        st.session_state.demo_mode       = True
        st.session_state.pipeline_paused = False
        st.session_state.paused_state    = None
        st.session_state.rag_ready       = False
        st.session_state.rag_assets      = {}
        st.session_state.show_figures    = False
        st.session_state.show_qa         = False
        st.session_state.qa_history      = []

        # Step 1: Show agent logs progressively to simulate a live run
        with st.status("🤖 Running demo analysis: Attention Is All You Need...", expanded=True) as demo_status:
            for log in ATTENTION_DEMO["agent_logs"]:
                st.write(f"{log['agent']} — {log['message']}")
                time.sleep(0.65)
            demo_status.update(label="✅ Demo analysis complete!", state="complete")

        st.session_state.result = ATTENTION_DEMO

        # Step 2: Load (or generate) figure/table assets for the demo paper.
        # First run: downloads the PDF, extracts images/tables, calls Gemini Vision
        #            for explanations, then caches everything.
        # Subsequent runs: loads from cache instantly — no API calls.
        demo_paper_id = "attention_1706_03762"
        cache_file    = CACHE_DIR / f"{demo_paper_id}_assets.json"

        if cache_file.exists():
            # Fast path: just load from cache and rebuild the RAG index
            try:
                from utils.figure_explainer import _load_cache
                from rag.embedder           import reset_and_build
                assets = _load_cache(demo_paper_id)
                if assets:
                    reset_and_build(assets)
                    st.session_state.rag_assets = assets
                    st.session_state.rag_ready  = True
            except Exception:
                pass  # Non-fatal — figures tab will show an info message
        else:
            # First run: download PDF, extract, explain, cache
            with st.status("🖼️ Extracting figures and tables (first run only)...", expanded=True) as fig_status:
                try:
                    from utils.arxiv_fetcher    import fetch_paper
                    from utils.figure_explainer import get_or_create_assets
                    from rag.embedder           import reset_and_build

                    st.write("📥 Downloading paper PDF from arXiv...")
                    paper    = fetch_paper("https://arxiv.org/abs/1706.03762")
                    temp_pdf = paper.get("pdf_path", "")

                    if not temp_pdf or not os.path.exists(temp_pdf):
                        fig_status.update(label="⚠ PDF unavailable — figures skipped.", state="error")
                    else:
                        # Copy temp PDF to a persistent path
                        CACHE_DIR.mkdir(parents=True, exist_ok=True)
                        persistent_pdf = CACHE_DIR / "attention_paper.pdf"
                        shutil.copy2(temp_pdf, str(persistent_pdf))

                        st.write("🔍 Extracting and explaining figures with AI...")
                        assets = get_or_create_assets(
                            str(persistent_pdf),
                            paper_id=demo_paper_id,
                        )
                        reset_and_build(assets)
                        st.session_state.rag_assets = assets
                        st.session_state.rag_ready  = True

                        n_figs = len(assets.get("figures", []))
                        n_tbls = len(assets.get("tables",  []))
                        fig_status.update(
                            label=f"✅ Extracted {n_figs} figures and {n_tbls} tables.",
                            state="complete",
                        )
                except Exception as e:
                    st.warning(f"Could not extract figures and tables: {e}")
                    fig_status.update(label="⚠ Extraction error.", state="error")

    if analyse_btn and query.strip():
        st.session_state.demo_mode       = False
        st.session_state.pipeline_paused = False
        st.session_state.paused_state    = None
        with st.status("🤖 Running 11-agent research pipeline…", expanded=True) as status:
            try:
                from graph.workflow import run_pipeline

                nodes = [
                    ("📄 Paper Fetcher",    "Fetching paper from arXiv…"),
                    ("📑 PDF Extractor",    "Extracting and parsing PDF…"),
                    ("🧭 Planner",          "Building research strategy…"),
                    ("📚 Research Agent",   "Reviewing related literature…"),
                    ("🔬 Critic Agent",     "Identifying weaknesses…"),
                    ("💡 Hypothesis Agent", "Generating research ideas…"),
                    ("📊 Repro Scorer",     "Scoring reproducibility…"),
                    ("💻 Code Agent",       "Writing implementation code…"),
                    ("🔍 Evidence Tracker", "Tracing claims to paper…"),
                    ("✨ Synthesizer",      "Generating final report…"),
                ]
                for name, msg in nodes:
                    st.write(f"{name} — {msg}")

                run_result = run_pipeline(query.strip())

                st.session_state.result          = run_result["state"]
                st.session_state.pipeline_paused = run_result["paused"]
                st.session_state.paused_state    = run_result["state"] if run_result["paused"] else None
                st.session_state.rag_ready       = False
                st.session_state.rag_assets      = {}
                st.session_state.show_figures    = False
                st.session_state.show_qa         = False
                st.session_state.qa_history      = []

                if run_result["paused"]:
                    status.update(
                        label="⚠ Keys exhausted — pipeline paused (see below to resume).",
                        state="error",
                    )
                else:
                    status.update(label="✅ Analysis complete!", state="complete")
            except Exception as e:
                status.update(label=f"❌ Error: {e}", state="error")
                st.error(f"Pipeline error: {e}")
                return

    # ── Key-exhausted resume dialog ───────────────────────────────────────────
    if st.session_state.get("pipeline_paused") and st.session_state.get("paused_state"):
        _render_key_exhausted_dialog()

    # ── Render results ────────────────────────────────────────────────────────
    state = st.session_state.result
    if state is None:
        st.divider()
        st.markdown("### Welcome to ResearchPilot AI 🔬")
        st.write(
            "Enter any arXiv paper title or URL above, or click **⚡ Demo** "
            "to try a pre-built analysis of *Attention Is All You Need*."
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.info("🤖 10 AI Research Agents")
        with col2:
            st.info("📊 Reproducibility Scoring")
        with col3:
            st.info("🎭 Agent Debate Feature")
        with col4:
            st.info("💻 Code Generation")
        return

    render_sidebar(state)

    if st.session_state.demo_mode:
        st.info(
            "⚡ **Demo Mode** — Showing pre-built analysis of "
            "*Attention Is All You Need* (Vaswani et al., 2017). "
            "Enter any paper above and click Analyse to run the live pipeline."
        )

    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Overview",
        "🔬 Deep Analysis",
        "🎭 Critique & Debate",
        "📊 Reproducibility",
        "💻 Try It Yourself",
        "💡 Research Ideas",
    ])

    with tab1:
        render_overview(state)
    with tab2:
        render_deep_analysis(state)
    with tab3:
        render_critique(state)
    with tab4:
        render_reproducibility(state)
    with tab5:
        render_code(state)
    with tab6:
        render_ideas(state)

    # ── Additional tools ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("**Additional Tools**")
    tb_col1, tb_col2, tb_spacer = st.columns([2, 2, 4])
    with tb_col1:
        fig_label = (
            "🖼️ Hide Figures & Tables"
            if st.session_state.show_figures
            else "🖼️ View Extracted Figures & Tables"
        )
        if st.button(fig_label, use_container_width=True, key="toggle_figures_btn"):
            st.session_state.show_figures = not st.session_state.show_figures
            if st.session_state.show_figures:
                st.session_state.show_qa = False
    with tb_col2:
        qa_label = (
            "💬 Hide Ask The Paper"
            if st.session_state.show_qa
            else "💬 Ask The Paper"
        )
        if st.button(qa_label, use_container_width=True, key="toggle_qa_btn"):
            st.session_state.show_qa = not st.session_state.show_qa
            if st.session_state.show_qa:
                st.session_state.show_figures = False

    if st.session_state.show_figures:
        render_figures_tables(state)

    if st.session_state.show_qa:
        render_ask_paper(state)


if __name__ == "__main__":
    main()

/**
 * main.js — ResearchPilot AI frontend (all phases combined)
 *
 * Sections:
 *  A. Agent definitions
 *  B. State & DOM refs
 *  C. Tab switching
 *  D. PDF file selection
 *  E. Agent cards
 *  F. renderResults()  — synthesis, papers, findings, hypotheses, errors
 *  G. renderCharts()   — Chart.js repro bar + timeline with auto-analysis
 *  H. renderTech()     — model profiles + code snippet
 *  I. Pipeline runners — arXiv, PDF, Demo
 *  J. Event listeners
 */


// ════════════════════════════════════════════════════════════════════════════
// A. AGENT DEFINITIONS
// ════════════════════════════════════════════════════════════════════════════

const ARXIV_AGENTS = [
  { id: "planner",     label: "Planner",      icon: "🗂️" },
  { id: "research",    label: "Research",      icon: "🔍" },
  { id: "critic",      label: "Critic",        icon: "🧐" },
  { id: "hypothesis",  label: "Hypothesis",    icon: "💡" },
  { id: "evaluator",   label: "Evaluator",     icon: "🎓" },
  { id: "memory",      label: "Memory",        icon: "🧠" },
  { id: "repro",       label: "Repro Scorer",  icon: "📊" },
  { id: "tech",        label: "Tech Analyzer", icon: "⚙️" },
  { id: "synthesizer", label: "Synthesizer",   icon: "✨" },
];

const PDF_AGENTS = ARXIV_AGENTS.filter(
  a => !["planner", "research"].includes(a.id)
);


// ════════════════════════════════════════════════════════════════════════════
// B. STATE & DOM REFS
// ════════════════════════════════════════════════════════════════════════════

let activeMode   = "arxiv";
let selectedFile = null;
let reproChart   = null;   // holds Chart.js instances so we can destroy & rebuild
let timelineChart = null;

const queryInput   = document.getElementById("query-input");
const runBtn       = document.getElementById("run-btn");
const tabArxiv     = document.getElementById("tab-arxiv");
const tabPdf       = document.getElementById("tab-pdf");
const panelArxiv   = document.getElementById("panel-arxiv");
const panelPdf     = document.getElementById("panel-pdf");
const dropZone     = document.getElementById("drop-zone");
const pdfInput     = document.getElementById("pdf-input");
const fileChosen   = document.getElementById("file-chosen");
const fileName     = document.getElementById("file-name");
const fileSize     = document.getElementById("file-size");
const clearFileBtn = document.getElementById("clear-file");
const uploadBtn    = document.getElementById("upload-btn");
const agentGrid    = document.getElementById("agent-grid");
const resultsPanel = document.getElementById("results-panel");


// ════════════════════════════════════════════════════════════════════════════
// C. TAB SWITCHING
// ════════════════════════════════════════════════════════════════════════════

function switchTab(mode) {
  activeMode = mode;
  const isArxiv = mode === "arxiv";
  tabArxiv.className = `tab-btn px-5 py-2 rounded-xl text-sm font-semibold transition-colors ${isArxiv ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"}`;
  tabPdf.className   = `tab-btn px-5 py-2 rounded-xl text-sm font-semibold transition-colors ${!isArxiv ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"}`;
  panelArxiv.classList.toggle("hidden", !isArxiv);
  panelPdf.classList.toggle("hidden",    isArxiv);
  agentGrid.classList.add("hidden");
  resultsPanel.classList.add("hidden");
}

tabArxiv.addEventListener("click", () => switchTab("arxiv"));
tabPdf.addEventListener("click",   () => switchTab("pdf"));


// ════════════════════════════════════════════════════════════════════════════
// D. PDF FILE SELECTION
// ════════════════════════════════════════════════════════════════════════════

function showFileChosen(file) {
  selectedFile = file;
  fileName.textContent = file.name;
  fileSize.textContent = `${(file.size / 1024).toFixed(0)} KB`;
  fileChosen.classList.remove("hidden");
  dropZone.classList.add("hidden");
}

function clearFile() {
  selectedFile = null;
  pdfInput.value = "";
  fileChosen.classList.add("hidden");
  dropZone.classList.remove("hidden");
}

dropZone.addEventListener("click", () => pdfInput.click());
pdfInput.addEventListener("change", () => { if (pdfInput.files[0]) showFileChosen(pdfInput.files[0]); });
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("border-indigo-500"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("border-indigo-500"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("border-indigo-500");
  const file = e.dataTransfer.files[0];
  if (file?.name.toLowerCase().endsWith(".pdf")) showFileChosen(file);
  else alert("Please drop a PDF file.");
});
clearFileBtn.addEventListener("click", clearFile);


// ════════════════════════════════════════════════════════════════════════════
// E. AGENT CARDS
// ════════════════════════════════════════════════════════════════════════════

const CARD_STYLES = {
  idle:    "border-gray-700 bg-gray-800 text-gray-500",
  running: "border-indigo-500 bg-indigo-950 text-indigo-300 animate-pulse",
  done:    "border-green-600  bg-green-950  text-green-300",
  error:   "border-red-600   bg-red-950    text-red-300",
};
const CARD_LABELS = { idle: "Waiting", running: "Running…", done: "Done", error: "Error" };

function buildCard(agent, state = "idle") {
  const el = document.createElement("div");
  el.id = `card-${agent.id}`;
  el.className = `rounded-xl border p-3 transition-all duration-300 ${CARD_STYLES[state]}`;
  el.innerHTML = `
    <div class="text-xl mb-1">${agent.icon}</div>
    <div class="font-semibold text-xs">${agent.label}</div>
    <div class="text-[10px] mt-1 opacity-70 card-status">${CARD_LABELS[state]}</div>
  `;
  return el;
}

function setCardState(agentId, state) {
  const card = document.getElementById(`card-${agentId}`);
  if (!card) return;
  card.className = `rounded-xl border p-3 transition-all duration-300 ${CARD_STYLES[state]}`;
  card.querySelector(".card-status").textContent = CARD_LABELS[state];
}

async function animateCards(agents) {
  agentGrid.innerHTML = "";
  agents.forEach(a => agentGrid.appendChild(buildCard(a, "idle")));
  agentGrid.classList.remove("hidden");
  for (const a of agents) {
    setCardState(a.id, "running");
    await new Promise(r => setTimeout(r, 320));
  }
}


// ════════════════════════════════════════════════════════════════════════════
// F. RENDER RESULTS (synthesis, papers, findings, hypotheses, errors)
// ════════════════════════════════════════════════════════════════════════════

function scoreColorClass(n) {
  if (n >= 8) return "bg-green-700 text-green-100";
  if (n >= 5) return "bg-yellow-700 text-yellow-100";
  return "bg-red-800 text-red-100";
}

function renderResults(data) {
  // PDF meta card
  const metaCard = document.getElementById("paper-meta-card");
  if (data.mode === "pdf" && data.paper_meta) {
    const m = data.paper_meta;
    document.getElementById("meta-title").textContent   = m.title;
    document.getElementById("meta-authors").textContent = Array.isArray(m.authors) ? m.authors.join(", ") : m.authors;
    document.getElementById("meta-pages").textContent   = `📄 ${m.page_count} pages`;
    document.getElementById("meta-words").textContent   = `✏️ ~${m.word_count?.toLocaleString()} words`;
    document.getElementById("meta-code").textContent    = m.code_mentions?.length ? `💻 ${m.code_mentions.length} code signal(s)` : "";
    document.getElementById("meta-data").textContent    = m.dataset_mentions?.length ? `🗂 ${m.dataset_mentions.length} dataset(s)` : "";
    metaCard.classList.remove("hidden");
  } else {
    metaCard.classList.add("hidden");
  }

  // Synthesis — Markdown → HTML
  document.getElementById("synthesis-body").innerHTML =
    marked.parse(data.synthesis || "_No summary was generated._");

  // Papers + scores
  const scoreMap = {};
  (data.repro_scores || []).forEach(s => { scoreMap[s.title] = s; });
  const papersList = document.getElementById("papers-list");
  papersList.innerHTML = "";
  (data.papers || []).forEach(p => {
    const s = scoreMap[p.title] || {};
    const score = s.score ?? "?";
    const card = document.createElement("div");
    card.className = "bg-gray-800 rounded-xl p-4 flex gap-4 items-start";
    card.innerHTML = `
      <div class="flex-shrink-0 w-12 h-12 rounded-xl ${scoreColorClass(score)}
                  flex flex-col items-center justify-center">
        <span class="text-lg font-bold leading-none">${score}</span>
        <span class="text-[9px] opacity-70">/10</span>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-white font-semibold text-sm leading-snug mb-0.5">
          ${p.url ? `<a href="${p.url}" target="_blank" class="hover:text-indigo-300 transition-colors">${p.title}</a>` : p.title}
        </p>
        <p class="text-gray-500 text-xs mb-1">
          ${Array.isArray(p.authors) ? p.authors.join(", ") : (p.authors || "")}
          ${p.published ? " · " + p.published : ""}
        </p>
        ${s.reasoning ? `<p class="text-gray-400 text-xs italic">${s.reasoning}</p>` : ""}
      </div>`;
    papersList.appendChild(card);
  });

  // Key findings
  const findingsList = document.getElementById("findings-list");
  findingsList.innerHTML = "";
  (data.key_findings || []).forEach(f => {
    const li = document.createElement("li");
    li.className = "flex gap-2";
    li.innerHTML = `<span class="text-indigo-400 mt-0.5 flex-shrink-0">▸</span><span>${f.replace(/^•\s*/, "")}</span>`;
    findingsList.appendChild(li);
  });

  // Hypotheses
  const hypoList = document.getElementById("hypotheses-list");
  hypoList.innerHTML = "";
  (data.hypotheses || []).forEach((h, i) => {
    const li = document.createElement("li");
    li.className = "flex gap-3";
    li.innerHTML = `
      <span class="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-900 text-indigo-300
                   text-xs flex items-center justify-center font-bold mt-0.5">${i + 1}</span>
      <span class="flex-1">${h.replace(/^H:\s*/i, "")}</span>`;
    hypoList.appendChild(li);
  });

  // Evaluator feedback badge
  const evalCard = document.getElementById("card-evaluator");
  if (evalCard && (data.hypothesis_iterations ?? 1) > 1) {
    if (!evalCard.querySelector(".loop-badge")) {
      const badge = document.createElement("div");
      badge.className = "loop-badge mt-1 text-[9px] bg-indigo-800 text-indigo-200 rounded px-1.5 py-0.5 inline-block";
      badge.textContent = `Refined ${data.hypothesis_iterations - 1}×`;
      evalCard.appendChild(badge);
    }
  }

  // Errors
  const errorsCard = document.getElementById("errors-card");
  const errorsList = document.getElementById("errors-list");
  const errs = data.errors || [];
  if (errs.length) {
    errorsList.innerHTML = errs.map(e => `<li>${e}</li>`).join("");
    errorsCard.classList.remove("hidden");
  } else {
    errorsCard.classList.add("hidden");
  }

  resultsPanel.classList.remove("hidden");
}


// ════════════════════════════════════════════════════════════════════════════
// G. CHARTS  (Chart.js — no extra API calls)
// ════════════════════════════════════════════════════════════════════════════

/**
 * Chart.js dark-mode defaults applied to every chart.
 * Chart.defaults lets us set these once instead of repeating in every config.
 */
Chart.defaults.color          = "#94a3b8";  // slate-400
Chart.defaults.borderColor    = "#1e293b";  // slate-800
Chart.defaults.backgroundColor = "#1e293b";

function scoreToColor(n, alpha = 1) {
  if (n >= 8) return `rgba(34,197,94,${alpha})`;   // green-500
  if (n >= 5) return `rgba(234,179,8,${alpha})`;   // yellow-500
  return `rgba(239,68,68,${alpha})`;                // red-500
}

function renderCharts(data) {
  const scores = data.repro_scores || [];
  const papers = data.papers || [];

  // ── Chart 1: Reproducibility Score (horizontal bar) ───────────────────
  const reproCtx = document.getElementById("chart-repro");
  if (reproChart) reproChart.destroy();

  if (scores.length) {
    const labels = scores.map(s => s.title.length > 22 ? s.title.slice(0, 22) + "…" : s.title);
    const values = scores.map(s => s.score ?? 0);
    const colors = values.map(v => scoreToColor(v, 0.85));

    reproChart = new Chart(reproCtx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Repro Score",
          data:  values,
          backgroundColor: colors,
          borderRadius: 6,
          borderSkipped: false,
        }],
      },
      options: {
        indexAxis: "y",        // horizontal bars
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.raw}/10 — ${scores[ctx.dataIndex]?.reasoning || ""}`,
            },
          },
        },
        scales: {
          x: { min: 0, max: 10, ticks: { stepSize: 2 }, grid: { color: "#1e293b" } },
          y: { grid: { display: false }, ticks: { font: { size: 10 } } },
        },
      },
    });

    // Auto-analysis text — narrative, not just stats
    const avg    = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1);
    const best   = scores.reduce((a, b) => (a.score ?? 0) >= (b.score ?? 0) ? a : b);
    const worst  = scores.reduce((a, b) => (a.score ?? 0) <= (b.score ?? 0) ? a : b);
    const lowCount = values.filter(v => v < 5).length;

    let reproAnalysis;
    if (values.length < 2) {
      reproAnalysis = "Not enough papers to compare — check the score badge on the paper card above.";
    } else if (parseFloat(avg) >= 7.5) {
      reproAnalysis =
        `This field is doing well on openness — average ${avg}/10 means most papers share their code and data. ` +
        `"${best.title.slice(0, 38)}…" (${best.score}/10) is the gold standard here: you can verify its claims yourself. ` +
        (best.score === worst.score
          ? "Scores are consistent — all papers are roughly equally open."
          : `"${worst.title.slice(0, 38)}…" (${worst.score}/10) is the one to double-check before building on it — ` +
            `it may be harder to reproduce than the others.`);
    } else if (parseFloat(avg) >= 5) {
      reproAnalysis =
        `Mixed picture — average ${avg}/10. Some papers share everything, others share very little. ` +
        (lowCount > 0
          ? `${lowCount} paper${lowCount > 1 ? "s" : ""} score below 5, which usually means no public code or dataset — ` +
            `you'd have to re-implement from scratch. `
          : "") +
        `Before using these as baselines, confirm "${worst.title.slice(0, 38)}…" (${worst.score}/10) ` +
        `has what you actually need.`;
    } else {
      reproAnalysis =
        `Reproducibility is a real concern here — average ${avg}/10 means most papers don't share ` +
        `enough for independent verification. Treat their benchmark numbers as directional, not definitive. ` +
        `"${best.title.slice(0, 38)}…" at ${best.score}/10 is the most open of the bunch — start there.`;
    }
    document.getElementById("chart-repro-analysis").textContent = reproAnalysis;
  }

  // ── Chart 2: Publication Timeline (scatter) ───────────────────────────
  const timeCtx = document.getElementById("chart-timeline");
  if (timelineChart) timelineChart.destroy();

  const paperPoints = papers
    .filter(p => p.published)
    .map(p => {
      const scoreObj = (data.repro_scores || []).find(s => s.title === p.title);
      return {
        x: new Date(p.published).getFullYear(),
        y: scoreObj?.score ?? 5,
        label: p.title,
      };
    });

  if (paperPoints.length) {
    timelineChart = new Chart(timeCtx, {
      type: "scatter",
      data: {
        datasets: [{
          label: "Papers",
          data:  paperPoints,
          backgroundColor: paperPoints.map(pt => scoreToColor(pt.y, 0.8)),
          pointRadius: 10,
          pointHoverRadius: 13,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => {
                const pt = paperPoints[ctx.dataIndex];
                return ` ${pt.label.slice(0, 45)} — ${pt.y}/10`;
              },
            },
          },
        },
        scales: {
          x: {
            type: "linear",
            title: { display: true, text: "Year Published", color: "#64748b" },
            ticks: { stepSize: 1, callback: v => v.toString() },
            grid: { color: "#1e293b" },
          },
          y: {
            title: { display: true, text: "Repro Score", color: "#64748b" },
            min: 0, max: 10,
            grid: { color: "#1e293b" },
          },
        },
      },
    });

    // Auto-analysis — narrative trend description
    const years   = paperPoints.map(p => p.x);
    const spanYrs = Math.max(...years) - Math.min(...years);
    const minYear = Math.min(...years);
    const maxYear = Math.max(...years);

    let timeAnalysis;
    if (paperPoints.length < 2) {
      timeAnalysis = "Not present — only one paper to plot, so there's no trend to show.";
    } else if (spanYrs === 0) {
      timeAnalysis = "Not present — all papers were published in the same year, so the chart can't show a trend over time.";
    } else if (spanYrs < 3) {
      const minScore = Math.min(...paperPoints.map(p => p.y));
      const maxScore = Math.max(...paperPoints.map(p => p.y));
      timeAnalysis =
        `Papers are clustered within a ${spanYrs}-year window (${minYear}–${maxYear}) — ` +
        `too short a gap to draw a meaningful trend. Scores range from ${minScore} to ${maxScore}/10 across this period.`;
    } else {
      const midYear = minYear + Math.floor(spanYrs / 2);
      const early   = paperPoints.filter(p => p.x <= midYear);
      const late    = paperPoints.filter(p => p.x > midYear);
      const earlyAvg = early.length ? (early.reduce((s, p) => s + p.y, 0) / early.length).toFixed(1) : null;
      const lateAvg  = late.length  ? (late.reduce((s, p)  => s + p.y, 0) / late.length).toFixed(1)  : null;

      if (earlyAvg && lateAvg) {
        if (parseFloat(lateAvg) > parseFloat(earlyAvg) + 0.5) {
          timeAnalysis =
            `Reproducibility is improving — earlier papers (${minYear}–${midYear}) averaged ${earlyAvg}/10, ` +
            `while more recent ones (${midYear + 1}–${maxYear}) average ${lateAvg}/10. ` +
            `The field is getting better at sharing code and data as time goes on.`;
        } else if (parseFloat(earlyAvg) > parseFloat(lateAvg) + 0.5) {
          timeAnalysis =
            `Older papers are actually more reproducible than the newer ones here — ` +
            `early work (${minYear}–${midYear}) averaged ${earlyAvg}/10 vs ${lateAvg}/10 for recent papers. ` +
            `This can happen when a field moves quickly and teams prioritise getting results out over sharing everything.`;
        } else {
          timeAnalysis =
            `Reproducibility has stayed roughly flat over ${spanYrs} years (${minYear}–${maxYear}) — ` +
            `early papers averaged ${earlyAvg}/10 and recent ones ${lateAvg}/10. ` +
            `There's no clear trend toward more or less openness over time in this area.`;
        }
      } else {
        timeAnalysis = `Papers span ${spanYrs} years (${minYear}–${maxYear}). Hover over each dot to see a paper's title and score.`;
      }
    }
    document.getElementById("chart-timeline-analysis").textContent = timeAnalysis;
  }
}


// ════════════════════════════════════════════════════════════════════════════
// H. RENDER TECH PROFILES + CODE SNIPPET
// ════════════════════════════════════════════════════════════════════════════

const PROFILE_FIELDS = [
  { key: "architecture",  label: "Architecture",    icon: "🏗️" },
  { key: "key_components",label: "Key components",  icon: "🔩" },
  { key: "parameters",   label: "Model size",       icon: "📐" },
  { key: "training_data",label: "Trained on",       icon: "📚" },
  { key: "compute",      label: "Compute needed",   icon: "🖥️" },
  { key: "framework",    label: "Framework",        icon: "🛠️" },
];

function renderTech(data) {
  // ── Model profiles ────────────────────────────────────────────────────
  const profilesEl = document.getElementById("tech-profiles");
  profilesEl.innerHTML = "";
  (data.model_profiles || []).forEach(prof => {
    const card = document.createElement("div");
    card.className = "bg-gray-800 rounded-xl p-4";
    const rows = PROFILE_FIELDS.map(f => {
      let val = prof[f.key];
      if (Array.isArray(val)) val = val.join(", ");
      if (!val || val === "Not specified" || val === "N/A") return "";
      return `
        <div class="flex gap-2 text-xs">
          <span class="text-gray-500 w-28 flex-shrink-0">${f.icon} ${f.label}</span>
          <span class="text-gray-200">${val}</span>
        </div>`;
    }).join("");

    card.innerHTML = `
      <p class="text-white font-semibold text-sm mb-3">${prof.paper || "Unknown paper"}</p>
      <div class="space-y-2">${rows}</div>`;
    profilesEl.appendChild(card);
  });

  // ── Code snippet ──────────────────────────────────────────────────────
  const codeContent = document.getElementById("code-content");
  const snippet     = (data.code_snippet || "# No code snippet was generated.").trim();
  codeContent.textContent = snippet;

  // Re-run Prism so it syntax-highlights the new content
  if (window.Prism) Prism.highlightElement(codeContent);

  // Copy button
  document.getElementById("copy-code-btn").onclick = () => {
    navigator.clipboard.writeText(snippet).then(() => {
      const btn = document.getElementById("copy-code-btn");
      btn.textContent = "Copied!";
      setTimeout(() => { btn.textContent = "Copy code"; }, 2000);
    });
  };
}


// ════════════════════════════════════════════════════════════════════════════
// I. RENDER METHODOLOGY, ASSUMPTIONS, WEAKNESSES
// ════════════════════════════════════════════════════════════════════════════

function renderAnalysis(data) {

  // ── Methodology ──────────────────────────────────────────────────────────
  const methodEl = document.getElementById("methodology-list");
  methodEl.innerHTML = "";
  (data.methodology || []).forEach(m => {
    const stepsHtml = (m.steps || []).length
      ? `<ol class="list-decimal list-inside space-y-1 mt-2 text-gray-400 text-xs">
           ${m.steps.map(s => `<li>${s}</li>`).join("")}
         </ol>`
      : "";
    const card = document.createElement("div");
    card.className = "bg-gray-800 rounded-xl p-4";
    card.innerHTML = `
      <p class="text-white font-semibold text-sm mb-2">${m.paper || "Unknown paper"}</p>
      <div class="space-y-1 text-xs">
        ${m.approach   ? `<p><span class="text-indigo-400 font-medium">Approach: </span><span class="text-gray-300">${m.approach}</span></p>` : ""}
        ${m.how_tested ? `<p><span class="text-indigo-400 font-medium">How tested: </span><span class="text-gray-300">${m.how_tested}</span></p>` : ""}
      </div>
      ${stepsHtml}`;
    methodEl.appendChild(card);
  });

  // ── Assumptions ──────────────────────────────────────────────────────────
  const assumpEl = document.getElementById("assumptions-list");
  assumpEl.innerHTML = "";
  (data.assumptions || []).forEach(a => {
    const card = document.createElement("div");
    card.className = "bg-gray-800 rounded-xl p-4";
    const rows = (a.assumptions || []).map(txt =>
      `<li class="flex gap-2"><span class="text-amber-400 flex-shrink-0 mt-0.5">⚠</span><span>${txt}</span></li>`
    ).join("");
    card.innerHTML = `
      <p class="text-white font-semibold text-sm mb-2">${a.paper || "Unknown paper"}</p>
      <ul class="space-y-1.5 text-xs text-gray-300">${rows}</ul>`;
    assumpEl.appendChild(card);
  });

  // ── Weaknesses ───────────────────────────────────────────────────────────
  const weakEl = document.getElementById("weaknesses-list");
  weakEl.innerHTML = "";
  (data.weaknesses || []).forEach(w => {
    const card = document.createElement("div");
    card.className = "bg-gray-800 rounded-xl p-4";
    const rows = (w.weaknesses || []).map(txt =>
      `<li class="flex gap-2"><span class="text-red-400 flex-shrink-0 mt-0.5">✕</span><span>${txt}</span></li>`
    ).join("");
    card.innerHTML = `
      <p class="text-white font-semibold text-sm mb-2">${w.paper || "Unknown paper"}</p>
      <ul class="space-y-1.5 text-xs text-gray-300">${rows}</ul>`;
    weakEl.appendChild(card);
  });
}


// ════════════════════════════════════════════════════════════════════════════
// K. PIPELINE RUNNERS
// ════════════════════════════════════════════════════════════════════════════

function _onSuccess(data, agents) {
  agents.forEach(a => setCardState(a.id, "done"));
  renderResults(data);
  renderCharts(data);
  renderTech(data);
  renderAnalysis(data);
}

async function runArxivPipeline() {
  const query = queryInput.value.trim();
  if (!query) { queryInput.focus(); return; }

  runBtn.disabled = true;
  runBtn.textContent = "Running…";
  resultsPanel.classList.add("hidden");
  await animateCards(ARXIV_AGENTS);

  try {
    const res  = await fetch("/api/research", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    if (data.status === "error") throw new Error(data.error);
    _onSuccess(data, ARXIV_AGENTS);
  } catch (err) {
    ARXIV_AGENTS.forEach(a => setCardState(a.id, "error"));
    alert(`Pipeline error: ${err.message}`);
  }

  runBtn.disabled = false;
  runBtn.textContent = "Analyze";
  resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}


async function runPdfPipeline() {
  if (!selectedFile) { alert("Please select a PDF first."); return; }

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Analyzing…";
  resultsPanel.classList.add("hidden");
  await animateCards(PDF_AGENTS);

  try {
    const form = new FormData();
    form.append("file", selectedFile);
    const res  = await fetch("/api/upload", { method: "POST", body: form });
    const data = await res.json();
    if (data.status === "error" || data.error) throw new Error(data.error || "Unknown error");
    _onSuccess(data, PDF_AGENTS);
  } catch (err) {
    PDF_AGENTS.forEach(a => setCardState(a.id, "error"));
    alert(`Upload error: ${err.message}`);
  }

  uploadBtn.disabled = false;
  uploadBtn.textContent = "Analyze Paper";
  resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}


async function runDemo() {
  const demoBtn = document.getElementById("demo-btn");
  demoBtn.disabled = true;
  demoBtn.innerHTML = "<span>⏳</span><span>Loading…</span>";

  switchTab("arxiv");
  queryInput.value = "Attention Is All You Need";
  resultsPanel.classList.add("hidden");
  await animateCards(ARXIV_AGENTS);

  try {
    const res  = await fetch("/api/demo");
    const data = await res.json();
    _onSuccess(data, ARXIV_AGENTS);
  } catch (err) {
    ARXIV_AGENTS.forEach(a => setCardState(a.id, "error"));
    alert(`Demo load error: ${err.message}`);
  }

  demoBtn.disabled = false;
  demoBtn.innerHTML = "<span>▶</span><span>Run Demo</span>";
  resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}


// ════════════════════════════════════════════════════════════════════════════
// L. EVENT LISTENERS
// ════════════════════════════════════════════════════════════════════════════

runBtn.addEventListener("click", runArxivPipeline);
queryInput.addEventListener("keydown", e => { if (e.key === "Enter") runArxivPipeline(); });
uploadBtn.addEventListener("click", runPdfPipeline);

const demoBtn = document.getElementById("demo-btn");
if (demoBtn) demoBtn.addEventListener("click", runDemo);

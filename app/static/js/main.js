/**
 * main.js — Frontend logic for ResearchPilot AI (Phase 3)
 *
 * Responsibilities:
 *  1. Tab switching between "Search arXiv" and "Upload PDF" modes.
 *  2. Drag-and-drop / click-to-browse PDF file selection.
 *  3. Animated agent status cards during pipeline execution.
 *  4. Rich results rendering (synthesis, papers, findings, hypotheses).
 */

// ── Agent definitions ─────────────────────────────────────────────────────────
const ARXIV_AGENTS = [
  { id: "planner",     label: "Planner",      icon: "🗂️" },
  { id: "research",    label: "Research",      icon: "🔍" },
  { id: "critic",      label: "Critic",        icon: "🧐" },
  { id: "hypothesis",  label: "Hypothesis",    icon: "💡" },
  { id: "memory",      label: "Memory",        icon: "🧠" },
  { id: "repro",       label: "Repro Scorer",  icon: "📊" },
  { id: "synthesizer", label: "Synthesizer",   icon: "✨" },
];

// PDF mode skips Planner + Research
const PDF_AGENTS = ARXIV_AGENTS.filter(
  a => !["planner", "research"].includes(a.id)
);

// ── DOM references ────────────────────────────────────────────────────────────
const tabArxiv      = document.getElementById("tab-arxiv");
const tabPdf        = document.getElementById("tab-pdf");
const panelArxiv    = document.getElementById("panel-arxiv");
const panelPdf      = document.getElementById("panel-pdf");

const queryInput    = document.getElementById("query-input");
const runBtn        = document.getElementById("run-btn");

const dropZone      = document.getElementById("drop-zone");
const pdfInput      = document.getElementById("pdf-input");
const fileChosen    = document.getElementById("file-chosen");
const fileName      = document.getElementById("file-name");
const fileSize      = document.getElementById("file-size");
const clearFileBtn  = document.getElementById("clear-file");
const uploadBtn     = document.getElementById("upload-btn");

const agentGrid     = document.getElementById("agent-grid");
const resultsPanel  = document.getElementById("results-panel");

// ── State ─────────────────────────────────────────────────────────────────────
let activeMode = "arxiv";   // "arxiv" | "pdf"
let selectedFile = null;


// ════════════════════════════════════════════════════════════════════════════
// TAB SWITCHING
// ════════════════════════════════════════════════════════════════════════════

function switchTab(mode) {
  activeMode = mode;

  const isArxiv = mode === "arxiv";

  // Active tab style
  tabArxiv.className = `tab-btn px-5 py-2 rounded-xl text-sm font-semibold transition-colors ${
    isArxiv ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"
  }`;
  tabPdf.className = `tab-btn px-5 py-2 rounded-xl text-sm font-semibold transition-colors ${
    !isArxiv ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"
  }`;

  panelArxiv.classList.toggle("hidden",  !isArxiv);
  panelPdf.classList.toggle("hidden",     isArxiv);

  // Reset results when switching tabs
  agentGrid.classList.add("hidden");
  resultsPanel.classList.add("hidden");
}

tabArxiv.addEventListener("click", () => switchTab("arxiv"));
tabPdf.addEventListener("click",   () => switchTab("pdf"));


// ════════════════════════════════════════════════════════════════════════════
// PDF FILE SELECTION (drag-and-drop + click-to-browse)
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

// Click the drop zone → open file picker
dropZone.addEventListener("click", () => pdfInput.click());

// File picker selection
pdfInput.addEventListener("change", () => {
  if (pdfInput.files[0]) showFileChosen(pdfInput.files[0]);
});

// Drag-and-drop
dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.classList.add("border-indigo-500", "bg-indigo-950/20");
});
dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("border-indigo-500", "bg-indigo-950/20");
});
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("border-indigo-500", "bg-indigo-950/20");
  const file = e.dataTransfer.files[0];
  if (file && file.name.toLowerCase().endsWith(".pdf")) {
    showFileChosen(file);
  } else {
    alert("Please drop a PDF file.");
  }
});

clearFileBtn.addEventListener("click", clearFile);


// ════════════════════════════════════════════════════════════════════════════
// AGENT CARDS
// ════════════════════════════════════════════════════════════════════════════

const STATE_STYLES = {
  idle:    "border-gray-700 bg-gray-800 text-gray-500",
  running: "border-indigo-500 bg-indigo-950 text-indigo-300 animate-pulse",
  done:    "border-green-600  bg-green-950  text-green-300",
  error:   "border-red-600   bg-red-950    text-red-300",
  skipped: "border-gray-800  bg-gray-900   text-gray-600",
};
const STATE_LABELS = {
  idle: "Waiting", running: "Running…", done: "Done", error: "Error", skipped: "Skipped",
};

function buildCard(agent, state = "idle") {
  const el = document.createElement("div");
  el.id = `card-${agent.id}`;
  el.className = `rounded-xl border p-4 transition-all duration-300 ${STATE_STYLES[state]}`;
  el.innerHTML = `
    <div class="text-2xl mb-1">${agent.icon}</div>
    <div class="font-semibold text-sm">${agent.label}</div>
    <div class="text-xs mt-1 opacity-70">${STATE_LABELS[state]}</div>
  `;
  return el;
}

function setCardState(agentId, state) {
  const card = document.getElementById(`card-${agentId}`);
  if (!card) return;
  card.className = `rounded-xl border p-4 transition-all duration-300 ${STATE_STYLES[state]}`;
  card.querySelector(".text-xs").textContent = STATE_LABELS[state];
}

async function animateCards(agents) {
  agentGrid.innerHTML = "";
  agents.forEach(a => agentGrid.appendChild(buildCard(a, "idle")));
  agentGrid.classList.remove("hidden");

  for (const a of agents) {
    setCardState(a.id, "running");
    await new Promise(r => setTimeout(r, 380));
  }
}


// ════════════════════════════════════════════════════════════════════════════
// RICH RESULTS RENDERING
// ════════════════════════════════════════════════════════════════════════════

/** Reproducibility score → colour class */
function scoreColor(n) {
  if (n >= 8) return "bg-green-700 text-green-100";
  if (n >= 5) return "bg-yellow-700 text-yellow-100";
  return "bg-red-800 text-red-100";
}

function renderResults(data) {
  // ── Synthesis (Markdown → HTML via marked.js) ──────────────────────
  const synthesisEl = document.getElementById("synthesis-body");
  synthesisEl.innerHTML = marked.parse(data.synthesis || "_No synthesis generated._");

  // ── PDF paper meta card ────────────────────────────────────────────
  const metaCard = document.getElementById("paper-meta-card");
  if (data.mode === "pdf" && data.paper_meta) {
    const m = data.paper_meta;
    document.getElementById("meta-title").textContent   = m.title;
    document.getElementById("meta-authors").textContent = Array.isArray(m.authors)
      ? m.authors.join(", ") : m.authors;
    document.getElementById("meta-pages").textContent =
      `📄 ${m.page_count} pages`;
    document.getElementById("meta-words").textContent =
      `✏️ ~${m.word_count.toLocaleString()} words`;
    document.getElementById("meta-code").textContent =
      m.code_mentions.length ? `💻 Code signals: ${m.code_mentions.length}` : "";
    document.getElementById("meta-data").textContent =
      m.dataset_mentions.length ? `🗂 Datasets: ${m.dataset_mentions.length}` : "";
    metaCard.classList.remove("hidden");
  } else {
    metaCard.classList.add("hidden");
  }

  // ── Papers + Repro Scores ──────────────────────────────────────────
  const papersList = document.getElementById("papers-list");
  papersList.innerHTML = "";

  // Build a quick title → score lookup
  const scoreMap = {};
  (data.repro_scores || []).forEach(s => { scoreMap[s.title] = s; });

  (data.papers || []).forEach(p => {
    const scoreObj = scoreMap[p.title] || {};
    const score    = scoreObj.score ?? "?";
    const reason   = scoreObj.reasoning || "";

    const card = document.createElement("div");
    card.className = "bg-gray-800 rounded-xl p-4 flex gap-4 items-start";
    card.innerHTML = `
      <div class="flex-shrink-0 w-12 h-12 rounded-xl ${scoreColor(score)}
                  flex flex-col items-center justify-center">
        <span class="text-xl font-bold leading-none">${score}</span>
        <span class="text-[9px] opacity-70">/ 10</span>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-white font-semibold text-sm leading-snug mb-1">
          ${p.url
            ? `<a href="${p.url}" target="_blank" rel="noopener"
                  class="hover:text-indigo-300 transition-colors">${p.title}</a>`
            : p.title}
        </p>
        <p class="text-gray-500 text-xs mb-1">
          ${Array.isArray(p.authors) ? p.authors.join(", ") : (p.authors || "")}
          ${p.published ? " · " + p.published : ""}
        </p>
        ${reason ? `<p class="text-gray-400 text-xs italic">${reason}</p>` : ""}
      </div>
    `;
    papersList.appendChild(card);
  });

  // ── Key Findings ───────────────────────────────────────────────────
  const findingsList = document.getElementById("findings-list");
  findingsList.innerHTML = "";
  (data.key_findings || []).forEach(f => {
    const li = document.createElement("li");
    li.className = "flex gap-2";
    li.innerHTML = `<span class="text-indigo-400 mt-0.5">▸</span><span>${f}</span>`;
    findingsList.appendChild(li);
  });

  // ── Hypotheses ─────────────────────────────────────────────────────
  const hypothesesList = document.getElementById("hypotheses-list");
  hypothesesList.innerHTML = "";
  (data.hypotheses || []).forEach((h, i) => {
    const li = document.createElement("li");
    li.className = "flex gap-3";
    li.innerHTML = `
      <span class="flex-shrink-0 w-6 h-6 rounded-full bg-indigo-900 text-indigo-300
                   text-xs flex items-center justify-center font-bold">${i + 1}</span>
      <span class="flex-1">${h.replace(/^H:\s*/i, "")}</span>
    `;
    hypothesesList.appendChild(li);
  });

  // ── Errors / Warnings ──────────────────────────────────────────────
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
  resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}


// ════════════════════════════════════════════════════════════════════════════
// PIPELINE RUNNERS
// ════════════════════════════════════════════════════════════════════════════

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

    ARXIV_AGENTS.forEach(a => setCardState(a.id, "done"));
    renderResults(data);
  } catch (err) {
    ARXIV_AGENTS.forEach(a => setCardState(a.id, "error"));
    alert(`Pipeline error: ${err.message}`);
  }

  runBtn.disabled = false;
  runBtn.textContent = "Analyze";
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

    if (data.status === "error" || data.error) {
      throw new Error(data.error || "Unknown error");
    }

    PDF_AGENTS.forEach(a => setCardState(a.id, "done"));
    renderResults(data);
  } catch (err) {
    PDF_AGENTS.forEach(a => setCardState(a.id, "error"));
    alert(`Upload error: ${err.message}`);
  }

  uploadBtn.disabled = false;
  uploadBtn.textContent = "Analyze Paper";
}


// ── Event listeners ───────────────────────────────────────────────────────────
runBtn.addEventListener("click", runArxivPipeline);
queryInput.addEventListener("keydown", e => { if (e.key === "Enter") runArxivPipeline(); });
uploadBtn.addEventListener("click", runPdfPipeline);

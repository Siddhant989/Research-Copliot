"""
app/routes/api.py — JSON API endpoints consumed by the frontend.

All routes here are prefixed with /api (set in app/__init__.py).

Endpoints:
  POST /api/research  — run the 7-agent arXiv pipeline
  POST /api/upload    — run the 5-agent PDF analysis pipeline
  GET  /api/status    — health check
"""

import os
import tempfile

from flask import Blueprint, request, jsonify

from app.agents.graph import run_pipeline, run_pdf_pipeline
from app.utils.pdf_parser import parse_pdf
from app.utils.graph_builder import build_graph_elements

api_bp = Blueprint("api", __name__)

MAX_PDF_BYTES = 15 * 1024 * 1024  # 15 MB hard limit


# ── POST /api/research ────────────────────────────────────────────────────────

@api_bp.route("/research", methods=["POST"])
def run_research():
    """
    Body:    { "query": "your research topic" }
    Returns: Full pipeline result as JSON, including `graph` for Cytoscape.
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "query field is required"}), 400

    try:
        result = run_pipeline(query)

        papers      = result.get("papers", [])
        repro_scores = result.get("repro_scores", [])

        return jsonify({
            "status":        "ok",
            "mode":          "arxiv",
            "query":         result.get("query", query),
            "refined_query": result.get("refined_query", ""),
            "papers":        papers,
            "critique":      result.get("critique", ""),
            "hypotheses":    result.get("hypotheses", []),
            "key_findings":  result.get("key_findings", []),
            "repro_scores":  repro_scores,
            "synthesis":     result.get("synthesis", ""),
            "errors":        result.get("errors", []),
            # Phase 5 — feedback loop telemetry
            "hypothesis_iterations": result.get("hypothesis_iterations", 1),
            "evaluator_feedback":    result.get("evaluator_feedback", ""),
            # Phase 4 — knowledge graph
            "graph":         build_graph_elements(papers, repro_scores),
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ── POST /api/upload ──────────────────────────────────────────────────────────

@api_bp.route("/upload", methods=["POST"])
def upload_pdf():
    """
    Accepts a multipart/form-data POST with a `file` field (PDF).
    Parses the PDF with PyMuPDF, then runs the 5-agent PDF pipeline.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file field in request. Send as multipart/form-data with key 'file'."}), 400

    uploaded = request.files["file"]

    if not uploaded.filename:
        return jsonify({"error": "No file selected."}), 400

    if not uploaded.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are accepted."}), 400

    # Check file size before reading
    uploaded.seek(0, 2)
    size = uploaded.tell()
    uploaded.seek(0)
    if size > MAX_PDF_BYTES:
        return jsonify({"error": f"PDF exceeds the 15 MB limit ({size // 1024 // 1024} MB uploaded)."}), 413

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    try:
        os.close(tmp_fd)
        uploaded.save(tmp_path)

        paper  = parse_pdf(tmp_path)
        result = run_pdf_pipeline(paper)

        papers       = [{k: v for k, v in paper.items() if k != "full_text"}]
        repro_scores = result.get("repro_scores", [])

        return jsonify({
            "status": "ok",
            "mode":   "pdf",
            "paper_meta": {
                "title":            paper["title"],
                "authors":          paper["authors"],
                "page_count":       paper["page_count"],
                "word_count":       paper["word_count"],
                "code_mentions":    paper["code_mentions"],
                "dataset_mentions": paper["dataset_mentions"],
            },
            "papers":        papers,
            "query":         result.get("query", paper["title"]),
            "refined_query": result.get("refined_query", ""),
            "critique":      result.get("critique", ""),
            "hypotheses":    result.get("hypotheses", []),
            "key_findings":  result.get("key_findings", []),
            "repro_scores":  repro_scores,
            "synthesis":     result.get("synthesis", ""),
            "errors":        result.get("errors", []),
            # Phase 5 — feedback loop telemetry
            "hypothesis_iterations": result.get("hypothesis_iterations", 1),
            "evaluator_feedback":    result.get("evaluator_feedback", ""),
            # Phase 4 — knowledge graph
            "graph":         build_graph_elements(papers, repro_scores),
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ── GET /api/status ───────────────────────────────────────────────────────────

@api_bp.route("/status", methods=["GET"])
def api_status():
    return jsonify({"status": "ok", "version": "0.5.0-phase5"})

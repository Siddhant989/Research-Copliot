"""
app/routes/api.py — JSON API endpoints consumed by the frontend.

All routes here are prefixed with /api (set in app/__init__.py).

Endpoints:
  POST /api/research  — run the full arXiv multi-agent pipeline
  POST /api/upload    — run the PDF analysis pipeline
  GET  /api/demo      — return pre-built demo results (no API key needed)
  GET  /api/status    — health check
"""

import os
import tempfile

from flask import Blueprint, request, jsonify

from app.agents.graph import run_pipeline, run_pdf_pipeline
from app.utils.pdf_parser import parse_pdf
from app.utils.demo_data import DEMO_RESULT

api_bp = Blueprint("api", __name__)

MAX_PDF_BYTES = 15 * 1024 * 1024  # 15 MB hard limit


def _format_result(result: dict, mode: str, query: str = "") -> dict:
    """Shared helper — builds the JSON response from a completed pipeline state."""
    return {
        "status":        "ok",
        "mode":          mode,
        "query":         result.get("query", query),
        "refined_query": result.get("refined_query", ""),
        "papers":        result.get("papers", []),
        "critique":      result.get("critique", ""),
        "hypotheses":    result.get("hypotheses", []),
        "key_findings":  result.get("key_findings", []),
        "repro_scores":  result.get("repro_scores", []),
        "model_profiles": result.get("model_profiles", []),
        "code_snippet":   result.get("code_snippet", ""),
        "methodology":    result.get("methodology", []),
        "assumptions":    result.get("assumptions", []),
        "weaknesses":     result.get("weaknesses",  []),
        "synthesis":     result.get("synthesis", ""),
        "hypothesis_iterations": result.get("hypothesis_iterations", 1),
        "evaluator_feedback":    result.get("evaluator_feedback", ""),
        "errors":        result.get("errors", []),
    }


# ── POST /api/research ────────────────────────────────────────────────────────

@api_bp.route("/research", methods=["POST"])
def run_research():
    """Body: { "query": "..." }  →  full pipeline result as JSON."""
    data  = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "query field is required"}), 400
    try:
        result = run_pipeline(query)
        return jsonify(_format_result(result, "arxiv", query))
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ── POST /api/upload ──────────────────────────────────────────────────────────

@api_bp.route("/upload", methods=["POST"])
def upload_pdf():
    """Accepts a PDF via multipart/form-data (key='file'), runs PDF pipeline."""
    if "file" not in request.files:
        return jsonify({"error": "No file field. Send multipart/form-data with key 'file'."}), 400

    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"error": "No file selected."}), 400
    if not uploaded.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are accepted."}), 400

    uploaded.seek(0, 2)
    size = uploaded.tell()
    uploaded.seek(0)
    if size > MAX_PDF_BYTES:
        return jsonify({"error": f"PDF exceeds 15 MB ({size // 1024 // 1024} MB)."}), 413

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    try:
        os.close(tmp_fd)
        uploaded.save(tmp_path)
        paper  = parse_pdf(tmp_path)
        result = run_pdf_pipeline(paper)

        payload = _format_result(result, "pdf", paper["title"])
        # Strip full_text from echoed papers (too large for JSON)
        payload["papers"] = [{k: v for k, v in paper.items() if k != "full_text"}]
        payload["paper_meta"] = {
            "title":            paper["title"],
            "authors":          paper["authors"],
            "page_count":       paper["page_count"],
            "word_count":       paper["word_count"],
            "code_mentions":    paper["code_mentions"],
            "dataset_mentions": paper["dataset_mentions"],
        }
        return jsonify(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ── GET /api/demo ─────────────────────────────────────────────────────────────

@api_bp.route("/demo", methods=["GET"])
def run_demo():
    """Returns pre-built demo results instantly — zero API calls."""
    return jsonify(DEMO_RESULT)


# ── GET /api/status ───────────────────────────────────────────────────────────

@api_bp.route("/status", methods=["GET"])
def api_status():
    return jsonify({"status": "ok", "version": "0.6.0"})

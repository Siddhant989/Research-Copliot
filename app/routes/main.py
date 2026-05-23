"""
app/routes/main.py — HTML page routes.

A Flask "Blueprint" is just a way to group related routes together.
This blueprint serves the browser-facing HTML pages.
"""

from flask import Blueprint, render_template

# Create the blueprint.  "main" is its internal name.
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Serve the main single-page application shell."""
    return render_template("index.html")


@main_bp.route("/health")
def health():
    """Simple liveness check — visit /health to confirm the server is up."""
    return {"status": "ok", "app": "ResearchPilot AI"}

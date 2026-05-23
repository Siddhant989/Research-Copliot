"""
run.py — Entry point for ResearchPilot AI.

To start the server:
    python run.py

Then open http://localhost:5000 in your browser.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True  → Flask auto-reloads when you save a file (great for dev)
    # host="0.0.0.0" → makes it reachable from other devices on the same Wi-Fi
    app.run(debug=True, host="0.0.0.0", port=5000)

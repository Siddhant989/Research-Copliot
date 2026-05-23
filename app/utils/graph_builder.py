"""
app/utils/graph_builder.py  — Turn pipeline output into a knowledge graph.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT IS A KNOWLEDGE GRAPH? (beginner explanation)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Imagine a corkboard with sticky notes and string:
  • Each sticky note = a THING  (a paper, a topic)
  • Each piece of string = a CONNECTION between two things

In code:
  • Things   → called NODES
  • Strings  → called EDGES

Our graph has two kinds of nodes:
  1. PAPER nodes  — one bubble per research paper, coloured by repro score
  2. TOPIC nodes  — one diamond per research area (e.g. "Machine Learning")

An EDGE is drawn whenever a paper belongs to a topic.
Two papers that share a topic will both connect to the same topic diamond,
making it visually obvious they are related.

Cytoscape.js (the JavaScript library) reads the list we build here and
draws everything on a canvas automatically.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ── Human-readable names for arXiv category codes ─────────────────────────────
# arXiv papers always carry category tags like "cs.LG" or "stat.ML".
# We map them to plain English so the graph labels are readable.
CATEGORY_LABELS = {
    "cs.LG":    "Machine Learning",
    "cs.CL":    "NLP",
    "cs.CV":    "Computer Vision",
    "cs.AI":    "Artificial Intelligence",
    "cs.NE":    "Neural Networks",
    "cs.IR":    "Information Retrieval",
    "cs.RO":    "Robotics",
    "cs.CR":    "Security",
    "cs.DS":    "Data Structures",
    "cs.DB":    "Databases",
    "cs.SE":    "Software Eng.",
    "cs.SI":    "Social Networks",
    "cs.HC":    "Human-Computer Int.",
    "cs.MM":    "Multimedia",
    "cs.GT":    "Game Theory",
    "cs.DC":    "Distributed Systems",
    "stat.ML":  "Statistical ML",
    "stat.AP":  "Applied Statistics",
    "eess.SP":  "Signal Processing",
    "eess.IV":  "Image & Video",
    "q-bio.QM": "Quantitative Biology",
    "math.OC":  "Optimization",
    "physics.data-an": "Data Analysis",
}


def _score_to_color(score) -> str:
    """
    Map a reproducibility score (0–10) to a hex colour.
      ≥ 8 → green  (well-reproducible)
      ≥ 5 → yellow (somewhat reproducible)
      < 5 → red    (poorly reproducible)
    """
    try:
        n = int(score)
    except (TypeError, ValueError):
        return "#6366f1"   # indigo fallback when score is unknown
    if n >= 8:
        return "#22c55e"   # green-500
    if n >= 5:
        return "#eab308"   # yellow-500
    return "#ef4444"        # red-500


def build_graph_elements(papers: list, repro_scores: list) -> dict:
    """
    Convert the list of papers + repro scores into Cytoscape.js element format.

    Cytoscape expects a list of dicts, each with a "data" key:
      Node: { "data": { "id": "...", "label": "...", ... } }
      Edge: { "data": { "id": "...", "source": "node-id", "target": "node-id" } }

    Args:
        papers:       List of paper dicts from the Research agent (or PDF parser).
        repro_scores: List of score dicts from the ReproScorer agent.

    Returns:
        { "nodes": [...], "edges": [...] }
        Both lists are already in the format Cytoscape.js understands.
    """
    nodes: list = []
    edges: list = []

    # Build a quick title → score lookup so we can colour each paper node
    score_map = {s["title"]: s.get("score", 5) for s in repro_scores}

    # Track which topic nodes we've already created (avoids duplicates)
    created_topics: set = set()

    for i, paper in enumerate(papers):
        paper_id    = f"paper-{i}"
        score       = score_map.get(paper["title"], 5)
        full_title  = paper.get("title", "Untitled")
        # Shorten the title so it fits inside the circle
        short_label = (full_title[:35] + "…") if len(full_title) > 35 else full_title

        # ── Paper node ────────────────────────────────────────────────────
        nodes.append({
            "data": {
                "id":         paper_id,
                "label":      short_label,
                "full_title": full_title,
                "type":       "paper",
                "score":      score,
                "color":      _score_to_color(score),
                "url":        paper.get("url", ""),
                "authors":    paper.get("authors", []),
                "published":  paper.get("published", ""),
            }
        })

        # ── Topic nodes + edges ───────────────────────────────────────────
        categories = paper.get("categories", [])

        # Use at most 2 categories per paper to keep the graph uncluttered
        for cat in categories[:2]:
            human_label = CATEGORY_LABELS.get(cat, cat)   # "cs.LG" → "Machine Learning"
            topic_id    = f"topic-{cat.replace('.', '-')}" # safe HTML id

            # Only create the topic node once even if many papers share it
            if topic_id not in created_topics:
                nodes.append({
                    "data": {
                        "id":    topic_id,
                        "label": human_label,
                        "type":  "topic",
                        "color": "#6366f1",   # indigo for all topic diamonds
                    }
                })
                created_topics.add(topic_id)

            # Draw a line: paper → topic
            edges.append({
                "data": {
                    "id":     f"e-{paper_id}-{topic_id}",
                    "source": paper_id,
                    "target": topic_id,
                }
            })

    return {"nodes": nodes, "edges": edges}

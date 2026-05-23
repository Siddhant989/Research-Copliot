"""
app/utils/arxiv_fetcher.py — Fetch research papers from arXiv.

arXiv is a free, open-access repository of scientific papers.
The `arxiv` Python library lets us search it programmatically.

Returns a list of plain dicts so the data is easy to JSON-serialize
and pass around between agents.
"""

import arxiv


def fetch_papers(query: str, max_results: int = 5) -> list[dict]:
    """
    Search arXiv and return a list of paper metadata dicts.

    Args:
        query:       Search string (e.g. "transformer attention NLP").
        max_results: How many papers to fetch (keep low to stay fast).

    Returns:
        List of dicts with keys: title, authors, abstract, url, published, categories.
        Returns an empty list on any error.
    """
    try:
        client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers = []
        for result in client.results(search):
            papers.append({
                "title":      result.title,
                "authors":    [a.name for a in result.authors[:5]],  # cap at 5 authors
                "abstract":   result.summary.replace("\n", " "),
                "url":        result.entry_id,
                "published":  str(result.published.date()),
                "categories": result.categories,
            })

        return papers

    except Exception as e:
        # Return an empty list rather than crashing the whole pipeline
        print(f"[arxiv_fetcher] Error fetching papers: {e}")
        return []

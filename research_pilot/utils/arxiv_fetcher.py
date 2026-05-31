import re, os, tempfile, urllib.request
import arxiv


def _extract_arxiv_id(text):

    # Search arXiv ID pattern in text
    match = re.search(
        r"arxiv\.org/(abs|pdf)/([0-9]{4}\.[0-9]+)",
        text
    )
    # If match found return ID
    if match:
        return match.group(2)

    # Otherwise return nothing
    return None


def _download_pdf(url):
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )
    file_path = temp_file.name
    try:
        urllib.request.urlretrieve(url, file_path)
        return file_path

    except Exception as e:
        temp_file.close()
        os.remove(file_path)
        raise e


def fetch_paper(query):
    client = arxiv.Client()
    arxiv_id = _extract_arxiv_id(query)
    if arxiv_id:
        search = arxiv.Search(id_list=[arxiv_id])
    else:
        # If ID is not there then we will search for our query 
        clean = query.strip().strip('"')
        search = arxiv.Search(
            query=f'ti:"{clean}"',
            max_results=3,
            sort_by=arxiv.SortCriterion.Relevance,
        )

    results = list(client.results(search))
    if not results:
        # Fallback: broader keyword search
        search = arxiv.Search(
            query=query,
            max_results=1,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = list(client.results(search))

    if not results:
        raise ValueError(f"No paper found for query: {query}")

    paper = results[0]

    # Download PDF
    pdf_url  = paper.pdf_url
    pdf_path = ""
    try:
        pdf_path = _download_pdf(pdf_url)
    except Exception:
        pass   # PDF download failure 

    return {
        "title":    paper.title,
        "abstract": paper.summary,
        "authors":  [a.name for a in paper.authors],
        "year":     str(paper.published.year) if paper.published else "",
        "url":      paper.entry_id,
        "arxiv_id": paper.get_short_id(),
        "pdf_path": pdf_path,
    }

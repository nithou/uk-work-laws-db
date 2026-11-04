# Regenerating the official-text folders

Requirements: Python 3, `lxml`, `markdownify`, `curl`; network access to legislation.gov.uk, www.acas.org.uk and www.gov.uk.

1. Legislation: for each line of `list.txt`, download `https://www.legislation.gov.uk/<id>/data.xml` into `raw/xml/<id with _>.xml`, then run `run_all.py` (edit the paths at the top). Revised XML includes annotations and the list of amendments not yet applied.
2. Acas: download the URLs of `https://www.acas.org.uk/sitemap.xml` (excluding about-us, research, podcasts, news) into `raw/acas/html/`, then run `acas2md.py` (keeps only advice, code-of-practice and guidance page types).
3. GOV.UK: build `links.json` from the Search API (`/api/search.json?filter_mainstream_browse_pages=working/...`) and run `govuk2md.py`, which reads the Content API.

Re-run every April (new rates) and after each Employment Rights Act 2025 commencement order.

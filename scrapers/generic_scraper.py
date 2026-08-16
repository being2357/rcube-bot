"""
Generic HTML listing scraper, driven entirely by config.HTML_SOURCES.

Each source entry supplies CSS selectors for:
  - item_selector: the repeated card/row element for one listing
  - title_selector: title text within that item
  - link_selector + link_attr: where to find the URL within that item

IMPORTANT: Real-world sites change their HTML often, and some (Unstop,
Internshala, LinkedIn, etc.) render content via JavaScript or actively
block simple scrapers. If a source returns 0 items:
  1. Open the page in a browser, view source, and update the selectors
     in config.py to match the current HTML.
  2. If content is JS-rendered, you'll need a headless browser (e.g.
     Playwright or Selenium) instead of requests+BeautifulSoup -- swap
     the `_fetch_html` function below for a Playwright-based fetch.
  3. Some sites require rotating a real browser User-Agent, or will
     block cloud/server IPs entirely -- consider using their own public
     API if one exists instead of scraping HTML.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import HTML_SOURCES, KEYWORDS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def _is_relevant(text: str) -> bool:
    text = (text or "").lower()
    return any(kw.lower() in text for kw in KEYWORDS)


def _fetch_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def fetch_html_events():
    results = []

    for src in HTML_SOURCES:
        try:
            html = _fetch_html(src["url"])
        except Exception as e:
            print(f"[generic_scraper] Failed to fetch {src['name']}: {e}")
            continue

        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(src["item_selector"])

        if not items:
            print(f"[generic_scraper] 0 items matched for {src['name']} "
                  f"-- selectors likely need updating (see module docstring).")
            continue

        for item in items:
            title_el = item.select_one(src["title_selector"])
            link_el = item.select_one(src["link_selector"])

            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            href = link_el.get(src["link_attr"], "")
            if not href:
                continue

            url = urljoin(src.get("base_url", src["url"]), href)

            # For sources that are already topic-specific (e.g. an
            # aerospace-only internship search URL), keep everything.
            # Otherwise filter by keyword relevance.
            if src.get("skip_keyword_filter") or _is_relevant(title):
                results.append({
                    "source": src["name"],
                    "title": title,
                    "url": url,
                    "summary": "",
                })

    return results

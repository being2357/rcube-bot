"""
Generic RSS/Atom feed scraper.

Works against any feed listed in config.RSS_SOURCES. Filters entries by
KEYWORDS so only aerospace / internship / hackathon / competition-relevant
items pass through.
"""

import feedparser
from config import RSS_SOURCES, KEYWORDS


def _is_relevant(text: str) -> bool:
    text = (text or "").lower()
    return any(kw.lower() in text for kw in KEYWORDS)


def fetch_rss_events():
    """Returns a list of dicts: source, title, url, summary."""
    results = []
    for src in RSS_SOURCES:
        try:
            feed = feedparser.parse(src["url"])
        except Exception as e:
            print(f"[rss_scraper] Failed to fetch {src['name']}: {e}")
            continue

        for entry in feed.entries:
            title = getattr(entry, "title", "") or ""
            summary = getattr(entry, "summary", "") or ""
            link = getattr(entry, "link", "") or ""

            if not link:
                continue

            if _is_relevant(title) or _is_relevant(summary):
                results.append({
                    "source": src["name"],
                    "title": title.strip(),
                    "url": link.strip(),
                    "summary": summary.strip()[:500],
                })
    return results

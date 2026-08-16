"""
Devpost hackathon source.

Devpost exposes a JSON endpoint (used by their own search UI) at
https://devpost.com/api/hackathons which accepts query params like
`search`, `status[]`, `page`. No API key required, but this is an
undocumented endpoint, so it may change without notice -- wrap in
try/except and don't rely on it as the only source.
"""

import requests
from config import DEVPOST_API, KEYWORDS

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AerospaceEventsBot/1.0)"}


def _is_relevant(text: str) -> bool:
    text = (text or "").lower()
    return any(kw.lower() in text for kw in KEYWORDS)


def fetch_devpost_hackathons():
    results = []
    queries = [
        {"search": "aerospace", "status[]": "upcoming"},
        {"search": "space", "status[]": "upcoming"},
        {"status[]": "open"},  # broad pass, filtered locally by keyword
    ]

    for params in queries:
        try:
            resp = requests.get(DEVPOST_API["url"], params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[devpost_scraper] Failed query {params}: {e}")
            continue

        for hack in data.get("hackathons", []):
            title = hack.get("title", "")
            url = hack.get("url", "")
            tagline = hack.get("displayed_location", {}).get("location", "") or hack.get("tagline", "")
            themes = " ".join(t.get("name", "") for t in hack.get("themes", []))

            haystack = f"{title} {tagline} {themes}"
            if not url:
                continue
            if _is_relevant(haystack):
                results.append({
                    "source": DEVPOST_API["name"],
                    "title": title.strip(),
                    "url": url.strip(),
                    "summary": (tagline or themes or "")[:500],
                })

    return results

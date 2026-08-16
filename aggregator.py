"""
Runs every configured scraper, dedupes against the DB, and stores new items.
Returns the list of genuinely new events found in this run.
"""

from database import add_event_if_new
from scrapers.rss_scraper import fetch_rss_events
from scrapers.devpost_scraper import fetch_devpost_hackathons
from scrapers.generic_scraper import fetch_html_events


def run_all_scrapers():
    all_events = []

    for fetch_fn, label in [
        (fetch_rss_events, "RSS"),
        (fetch_devpost_hackathons, "Devpost API"),
        (fetch_html_events, "HTML listings"),
    ]:
        try:
            events = fetch_fn()
            print(f"[aggregator] {label}: fetched {len(events)} candidate items")
            all_events.extend(events)
        except Exception as e:
            print(f"[aggregator] {label} failed entirely: {e}")

    new_events = []
    for ev in all_events:
        is_new = add_event_if_new(ev["source"], ev["title"], ev["url"], ev.get("summary", ""))
        if is_new:
            new_events.append(ev)

    print(f"[aggregator] {len(new_events)} new events stored this run")
    return new_events

# test_scraper.py
from scrapers.rss_scraper import scrape_rss
import config

print('Testing RSS scrapers...')
print(f'Found {len(config.RSS_SOURCES)} sources to check\n')

for source in config.RSS_SOURCES:
    print(f'Checking {source["name"]}...')
    try:
        events = scrape_rss(source['url'])
        print(f'✅ Found {len(events)} events')
        for event in events[:3]:  # Show first 3 events
            print(f'   - {event.get("title", "No title")[:50]}')
        print()
    except Exception as e:
        print(f'❌ Error: {e}\n')
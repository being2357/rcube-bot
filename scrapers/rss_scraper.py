import feedparser
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def scrape_rss(url):
    """
    Scrape an RSS feed and return list of events.
    This is the main function called by the aggregator.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Try to fetch with requests first (better headers)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
        except:
            # Fallback to direct feedparser
            feed = feedparser.parse(url)
        
        events = []
        
        for entry in feed.entries[:10]:  # Get latest 10 entries
            # Get description
            description = ''
            if hasattr(entry, 'description'):
                description = entry.description
            elif hasattr(entry, 'summary'):
                description = entry.summary
            elif hasattr(entry, 'content'):
                if isinstance(entry.content, list) and len(entry.content) > 0:
                    description = entry.content[0].get('value', '')
            
            # Clean description (remove HTML tags)
            if description:
                import re
                description = re.sub(r'<[^>]+>', ' ', description)
                description = ' '.join(description.split())[:300]  # Limit length
            
            # Get date
            pub_date = ''
            if hasattr(entry, 'published'):
                pub_date = entry.published
            elif hasattr(entry, 'updated'):
                pub_date = entry.updated
            elif hasattr(entry, 'date'):
                pub_date = str(entry.date)
            
            # Get link
            link = ''
            if hasattr(entry, 'link'):
                link = entry.link
            
            events.append({
                'title': entry.get('title', 'Untitled').strip(),
                'description': description,
                'link': link,
                'date': pub_date,
                'source': 'RSS'
            })
        
        logger.info(f"Scraped {len(events)} events from {url}")
        return events
        
    except Exception as e:
        logger.error(f"Error scraping RSS {url}: {e}")
        return []


def scrape_rss_feed(url):
    """
    Alias for scrape_rss for backward compatibility.
    """
    return scrape_rss(url)


# If you have any other functions, keep them here
# For example, if you had a different function name:
def fetch_rss_events(url):
    """Alternative name for scrape_rss"""
    return scrape_rss(url)
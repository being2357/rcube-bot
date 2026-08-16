"""
Central configuration for the Aerospace Events/Internships/Hackathons bot.

Edit SOURCES to add/remove where data comes from.
Edit KEYWORDS to change what counts as "relevant".
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Database ---
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "events.db")

# --- Scraping schedule ---
SCRAPE_INTERVAL_MINUTES = 60          # how often to check sources for new items
DAILY_DIGEST_HOUR = 8                 # 24h clock, server-local time
DAILY_DIGEST_MINUTE = 0

# --- Relevance filter ---
# An item is kept if its title/summary contains at least one keyword from
# EACH non-empty group below is NOT required — it's an OR match across all
# keywords (simple, easy to tune). Case-insensitive.
KEYWORDS = [
    # aerospace / space
    "aerospace", "aeronautics", "astronautics", "space", "satellite",
    "rocket", "propulsion", "avionics", "uav", "drone", "spaceflight",
    "aviation", "aircraft", "isro", "nasa", "esa", "spacex", "aiaa",
    # internships
    "internship", "intern ", "traineeship", "co-op",
    # competitions / hackathons
    "hackathon", "competition", "challenge", "contest", "cansat",
    "rocketry", "design competition",
]

# --- RSS / feed sources (generic, robust) ---
# Add any site that publishes an RSS/Atom feed here.
RSS_SOURCES = [
    {"name": "NASA News", "url": "https://www.nasa.gov/news-release/feed/"},
    {"name": "NASA STEM Opportunities", "url": "https://www.nasa.gov/stem-content-feed/feed/"},
    {"name": "SpaceNews", "url": "https://spacenews.com/feed/"},
    {"name": "AIAA News", "url": "https://www.aiaa.org/news/rss"},
    {"name": "ESA Rss", "url": "https://www.esa.int/rssfeed/Our_Activities"},
    {"name": "Space.com", "url": "https://www.space.com/feeds/all"},
]

# --- API-based sources ---
# Devpost has a public JSON search endpoint used by its own site search.
DEVPOST_API = {
    "name": "Devpost Hackathons",
    "url": "https://devpost.com/api/hackathons",
    "params": {"search": "aerospace"},  # also queried with a broad status=upcoming pass
}

# --- Generic HTML listing scrapers ---
# Each entry describes ONE listing page + CSS selectors to pull items out.
# You will very likely need to adjust selectors after inspecting the live
# page HTML (site layouts change often) -- see scrapers/generic_scraper.py.
HTML_SOURCES = [
    {
        "name": "Unstop (Competitions)",
        "url": "https://unstop.com/competitions",
        "item_selector": "div.card-wrapper",         # container per listing card
        "title_selector": "div.content h2",           # title inside container
        "link_selector": "a",                          # link inside container
        "link_attr": "href",
        "base_url": "https://unstop.com",
    },
    {
        "name": "Internshala (Aerospace Internships)",
        "url": "https://internshala.com/internships/aerospace-internship",
        "item_selector": "div.individual_internship",
        "title_selector": "h3.job-internship-name",
        "link_selector": "a.view_detail_button",
        "link_attr": "href",
        "base_url": "https://internshala.com",
    },
]

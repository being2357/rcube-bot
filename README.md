# Aerospace Events & Internships Bot

A Telegram bot that scrapes/pulls aerospace-related **events, internships,
hackathons, and competitions** from the web and RSS/APIs, then pushes new
finds instantly and sends a daily digest.

## What it does

- **Sources data** from:
  - RSS/Atom feeds (NASA, ESA, AIAA, SpaceNews, Space.com) — robust, rarely breaks
  - Devpost's hackathon search API — for hackathons
  - Configurable HTML page scraping (Unstop, Internshala) — for competitions/internships
- **Filters** everything through a keyword list (aerospace, internship,
  hackathon, competition, etc. — edit in `config.py`)
- **Dedupes** against a local SQLite database so you never get the same item twice
- **Notifies** subscribers on Telegram:
  - Instant ping when something new is found
  - One daily digest of everything from the last 24h

## 1. Get a Telegram bot token

1. Open Telegram, message **@BotFather**
2. Send `/newbot`, follow the prompts, copy the token it gives you

## 2. Set up the project

```bash
cd aerospace_bot
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your token:
# TELEGRAM_BOT_TOKEN=123456789:AA...
```

## 3. Run it

```bash
python main.py
```

Then in Telegram, open a chat with your bot and send `/start`.

Commands available to users:
- `/start` — subscribe + see help
- `/latest` — see everything found in the last 24h, on demand
- `/pause` / `/resume` — toggle instant pings (digest keeps coming either way)
- `/unsubscribe` — stop everything

## 4. IMPORTANT — about the scrapers

This was built and unit-tested for logic (deduplication, filtering,
storage, Telegram commands) in a sandboxed environment **without live
internet access to the target sites**. You will need to do a first live
test run yourself and expect to tweak two things:

### RSS sources (`config.py` → `RSS_SOURCES`)
These are the most reliable — RSS structure rarely changes. If one stops
returning items, the feed URL itself may have moved; search `"<site> RSS feed"`
to find the current one.

### HTML sources (`config.py` → `HTML_SOURCES`)
Sites like Unstop and Internshala change their page structure often, and
some load content via JavaScript, which plain scraping (`requests` +
`BeautifulSoup`) cannot see. If a source logs `0 items matched`:
1. Open the page in a browser → View Page Source
2. Find the repeating "card" element for one listing, and update
   `item_selector`, `title_selector`, `link_selector` in `config.py` to match
3. If the content isn't in the page source at all (only appears after the
   page finishes loading in a browser), it's JavaScript-rendered — swap
   `scrapers/generic_scraper.py`'s `_fetch_html()` for a headless-browser
   fetch using **Playwright** (`pip install playwright`, then
   `playwright install chromium`) instead of `requests`.

### Adding more sources
- **Got an RSS feed?** Just add `{"name": ..., "url": ...}` to `RSS_SOURCES`.
- **Got a JSON API?** Copy the pattern in `scrapers/devpost_scraper.py`.
- **Only have a webpage?** Copy the pattern in `HTML_SOURCES` + reuse
  `scrapers/generic_scraper.py`.

Good aerospace-specific sources worth adding once you inspect their real
markup: AIAA competitions page, ISRO careers/announcements, ESA vacancies,
Space Foundation, your university's aerospace department newsletter, MLH
(Major League Hacking) event list, CanSat competition site.

## 5. Deploying so it runs 24/7

Running `python main.py` on your laptop only works while it's open. To
keep it running continuously, deploy it on:
- A small VPS (DigitalOcean, Linode, etc.) with `systemd` or `tmux`/`screen`
- A free-tier platform like **Railway** or **Render** (background worker, not web service)
- A Raspberry Pi at home

On any of these, just set `TELEGRAM_BOT_TOKEN` as an environment variable
and run `python main.py` (or `pip install -r requirements.txt && python main.py`
as the start command).

## 6. Tuning behavior

All in `config.py`:
- `KEYWORDS` — what counts as "relevant" (currently aerospace + internship +
  hackathon + competition terms)
- `SCRAPE_INTERVAL_MINUTES` — how often to check for new items (default: 60)
- `DAILY_DIGEST_HOUR` / `DAILY_DIGEST_MINUTE` — when the daily digest goes out
  (server-local time, default 8:00 AM)

## Project structure

```
aerospace_bot/
├── main.py              # entrypoint — starts bot + scheduler
├── bot.py                # Telegram command handlers
├── scheduler.py          # scrape job + daily digest job
├── aggregator.py         # runs all scrapers, dedupes, stores
├── database.py           # SQLite storage (events + subscribers)
├── config.py             # sources, keywords, schedule — EDIT THIS FIRST
├── scrapers/
│   ├── rss_scraper.py       # RSS/Atom feeds
│   ├── devpost_scraper.py   # Devpost hackathon API
│   └── generic_scraper.py   # configurable HTML page scraping
├── requirements.txt
└── .env.example
```

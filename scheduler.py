"""
Background jobs, run via APScheduler inside the same event loop as the bot:

  1. scrape_job    - every SCRAPE_INTERVAL_MINUTES: run all scrapers, push
                      newly found events to subscribers who have pings on.
  2. digest_job    - once a day at DAILY_DIGEST_HOUR:DAILY_DIGEST_MINUTE:
                      send everyone a summary of the last 24h.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application
from telegram.error import Forbidden, BadRequest

import database as db
from aggregator import run_all_scrapers
from bot import _format_event
from config import SCRAPE_INTERVAL_MINUTES, DAILY_DIGEST_HOUR, DAILY_DIGEST_MINUTE

logger = logging.getLogger(__name__)


async def scrape_job(app: Application):
    new_events = run_all_scrapers()
    if not new_events:
        return

    subscribers = db.get_all_subscribers(push_only=True)
    for ev in new_events:
        text = _format_event(ev)
        for chat_id in subscribers:
            try:
                await app.bot.send_message(
                    chat_id=chat_id, text=text, parse_mode="Markdown",
                    disable_web_page_preview=True,
                )
            except Forbidden:
                # user blocked the bot -- clean up
                db.remove_subscriber(chat_id)
            except BadRequest as e:
                logger.warning(f"Failed to message {chat_id}: {e}")


async def digest_job(app: Application):
    events = db.get_events_last_n_hours(24)
    subscribers = db.get_all_subscribers(push_only=False)

    if not events:
        summary_text = "📋 Daily digest: nothing new in the last 24 hours."
    else:
        summary_text = f"📋 Daily digest: {len(events)} item(s) in the last 24 hours."

    for chat_id in subscribers:
        try:
            await app.bot.send_message(chat_id=chat_id, text=summary_text)
            for ev in events[:30]:
                await app.bot.send_message(
                    chat_id=chat_id, text=_format_event(ev),
                    parse_mode="Markdown", disable_web_page_preview=True,
                )
        except Forbidden:
            db.remove_subscriber(chat_id)
        except BadRequest as e:
            logger.warning(f"Failed to message {chat_id}: {e}")


def build_scheduler(app: Application) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        scrape_job, "interval", minutes=SCRAPE_INTERVAL_MINUTES,
        args=[app], id="scrape_job", next_run_time=None,
    )
    scheduler.add_job(
        digest_job, "cron", hour=DAILY_DIGEST_HOUR, minute=DAILY_DIGEST_MINUTE,
        args=[app], id="digest_job",
    )

    return scheduler

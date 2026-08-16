"""
Telegram bot: user-facing commands.

Commands:
  /start      - subscribe + show help
  /subscribe  - start receiving push updates + daily digest
  /unsubscribe- stop all updates
  /pause      - stop push updates but keep daily digest
  /resume     - resume push updates
  /latest     - show events found in the last 24h, on demand
  /help       - show help
"""

from telegram import Update
from telegram.ext import ContextTypes

import database as db


def _format_event(ev) -> str:
    # ev can be a tuple (source, title, url, summary) or dict-like
    if isinstance(ev, dict):
        source, title, url, summary = ev["source"], ev["title"], ev["url"], ev.get("summary", "")
    else:
        source, title, url, summary = ev
    line = f"🚀 *{title}*\nSource: {source}\n{url}"
    if summary:
        clean_summary = summary.replace("\n", " ").strip()
        if clean_summary:
            line += f"\n_{clean_summary[:200]}_"
    return line


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or ""
    db.add_subscriber(chat_id, username)
    await update.message.reply_text(
        "👋 Welcome! You're subscribed to aerospace events, internships, "
        "hackathons, and competitions.\n\n"
        "You'll get:\n"
        "• Instant pings when something new is found\n"
        "• A daily digest\n\n"
        "Commands:\n"
        "/latest — see what's new in the last 24h\n"
        "/pause — stop instant pings (keep daily digest)\n"
        "/resume — resume instant pings\n"
        "/unsubscribe — stop everything\n",
        parse_mode="Markdown",
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or ""
    db.add_subscriber(chat_id, username)
    await update.message.reply_text("✅ Subscribed. You'll get instant pings and a daily digest.")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db.remove_subscriber(chat_id)
    await update.message.reply_text("❌ Unsubscribed. Send /start any time to rejoin.")


async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db.set_push_enabled(chat_id, False)
    await update.message.reply_text("⏸ Instant pings paused. Daily digest will continue.")


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db.set_push_enabled(chat_id, True)
    await update.message.reply_text("▶️ Instant pings resumed.")


async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = db.get_events_last_n_hours(24)
    if not events:
        await update.message.reply_text("Nothing new in the last 24 hours. Check back later!")
        return

    await update.message.reply_text(f"Found {len(events)} item(s) in the last 24h:")
    for ev in events[:20]:  # avoid flooding
        await update.message.reply_text(_format_event(ev), parse_mode="Markdown", disable_web_page_preview=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

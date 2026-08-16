"""
Entrypoint. Run with:  python main.py

Requires TELEGRAM_BOT_TOKEN set in .env (see .env.example).
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Load .env file only if it exists (for local development)
if os.path.exists('.env'):
    load_dotenv()

# Check if token is set
if not os.getenv('TELEGRAM_BOT_TOKEN'):
    print("❌ ERROR: TELEGRAM_BOT_TOKEN not found!")
    print("Please set it in:")
    print("  - .env file (for local testing), or")
    print("  - GitHub Secrets (for GitHub Actions)")
    sys.exit(1)

print(f"✅ Bot token found: {os.getenv('TELEGRAM_BOT_TOKEN')[:10]}...")

from telegram.ext import Application, CommandHandler

import database as db
import bot
from scheduler import build_scheduler
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and "
            "fill in the token you got from @BotFather."
        )

    db.init_db()

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("subscribe", bot.subscribe))
    app.add_handler(CommandHandler("unsubscribe", bot.unsubscribe))
    app.add_handler(CommandHandler("pause", bot.pause))
    app.add_handler(CommandHandler("resume", bot.resume))
    app.add_handler(CommandHandler("latest", bot.latest))
    app.add_handler(CommandHandler("help", bot.help_command))

    scheduler = build_scheduler(app)

    async def _on_startup(app):
        scheduler.start()

    app.post_init = _on_startup

    print("Bot starting... press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()

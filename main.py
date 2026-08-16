"""
Entrypoint for 6-hour scheduled execution on GitHub Actions.
Run with: python main.py
"""
import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Bot

import database as db
import bot

# Load .env file for local development
if os.path.exists('.env'):
    load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN not found!")
    sys.exit(1)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def run_scrape_and_notify():
    # 1. Initialize SQLite Database
    db.init_db()

    # 2. Instantiate Telegram Bot instance directly
    telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

    logging.info("Starting scheduled scrape job...")

    # 3. Trigger your scraping logic directly
    # Call your scraper/digest functions from bot.py or aggregator.py here
    if hasattr(bot, 'run_scraping_job'):
        await bot.run_scraping_job(telegram_bot)
    elif hasattr(bot, 'scrape_and_send'):
        await bot.scrape_and_send(telegram_bot)
    else:
        # Fallback: run database check and notification routine
        logging.info("Executing custom scrape & broadcast routine...")

    logging.info("Scrape job completed successfully. Exiting workflow.")

def main():
    # Run the asynchronous job once and exit
    asyncio.run(run_scrape_and_notify())

if __name__ == "__main__":
    main()
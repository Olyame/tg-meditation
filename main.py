"""
Telegram Bot for Daily Meditation Reminders
Sends a reminder every morning at 8 AM to do meditation.
"""

import logging
import asyncio
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, AIORateLimiter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Store chat IDs of users who started the bot
subscribed_users = set()

# Meditation reminder message
MEDITATION_MESSAGE = """
🌅 Guten Morgen! 🌅

It's time for your daily meditation session.

🧘 Find a comfortable position
🌬️ Take deep breaths
💭 Clear your mind
⏱️ Spend 10-15 minutes in peace

Quiet the mind, and the soul will speak.

Enjoy your meditation! 🙏

I'm with you. O. <3
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - subscribe user to daily reminders."""
    chat_id = update.effective_chat.id
    subscribed_users.add(chat_id)
    await update.message.reply_text(
        "🧘 Welcome to Meditation Reminder Bot! 🧘\n\n"
        "You'll receive a daily reminder at 8 AM to do your meditation.\n"
        "Use /stop to unsubscribe from reminders."
    )
    logger.info(f"User {chat_id} subscribed to meditation reminders")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command - unsubscribe user from daily reminders."""
    chat_id = update.effective_chat.id
    subscribed_users.discard(chat_id)
    await update.message.reply_text(
        "You've been unsubscribed from daily meditation reminders.\n"
        "Use /start to subscribe again."
    )
    logger.info(f"User {chat_id} unsubscribed from meditation reminders")


async def send_meditation_reminder(application):
    """Send meditation reminder to all subscribed users."""
    for chat_id in subscribed_users:
        try:
            await application.bot.send_message(
                chat_id=chat_id,
                text=MEDITATION_MESSAGE
            )
            logger.info(f"Sent meditation reminder to user {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send message to user {chat_id}: {e}")
            # Remove invalid chat_id
            subscribed_users.discard(chat_id)


async def send_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a test message to verify the bot is working."""
    chat_id = update.effective_chat.id
    await update.message.reply_text("🧘 Test message: Your meditation reminder bot is working!")
    logger.info(f"Sent test message to user {chat_id}")


async def main():
    """Main function to run the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return

    # Create the Application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('test', send_test))

    # Create scheduler
    scheduler = AsyncIOScheduler()

    # Schedule meditation reminder at 8:40 AM daily (local time)
    scheduler.add_job(
        send_meditation_reminder,
        CronTrigger(hour=8, minute=40),
        args=[application],
        id='meditation_reminder',
        name='Daily meditation reminder at 8:40 AM'
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started - meditation reminders will be sent at 8:40 AM daily")

    # Run the bot
    logger.info("Starting Telegram bot...")
    await application.run_polling()


def run_bot():
    """Run the bot in a new event loop."""
    asyncio.run(main())


if __name__ == '__main__':
    # Run in a separate thread to avoid event loop conflicts
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Keep the main thread alive
    try:
        bot_thread.join()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

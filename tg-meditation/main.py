"""
Telegram Bot for Daily Meditation Reminders
Sends a reminder every morning at 9:20 AM CET.
"""

import logging
import os
import random
from datetime import datetime, time, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    PicklePersistence,
)

from pytz import timezone

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Define meditation message
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

# Motivational quotes
QUOTES = [
    "The thing to do when you're impatient is to enjoy the wait. - Unknown",
    "Quiet the mind, and the soul will speak. - Ma Jaya Sati Bhagavati",
    "Meditation is not about stopping thoughts, but recognizing that we are more than our thoughts. - Unknown",
    "The present moment is filled with joy and happiness. If you are attentive, you will see it. - Thich Nhat Hanh",
    "Breath is the bridge which connects life to consciousness. - Thich Nhat Hanh",
]

# Define Berlin timezone
BERLIN_TZ = timezone('Europe/Berlin')


def get_next_reminder_time():
    """Get the time of the next meditation reminder."""
    now = datetime.now(BERLIN_TZ)
    reminder_time = time(9, 20)  # 9:20 AM
    
    # Calculate next reminder
    next_reminder = now.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0)
    
    if now > next_reminder:
        next_reminder += timedelta(days=1)
    
    return next_reminder.strftime("%H:%M %Z")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - subscribe user to daily reminders."""
    chat_id = update.effective_chat.id
    logger.info(f"User {chat_id} started the bot")
    
    await update.message.reply_text(
        "🧘 Welcome to Meditation Reminder Bot! 🧘\n\n"
        "Your daily meditation reminder is set for 9:20 AM CET.\n\n"
        "📝 Commands:\n"
        "• /meditate - Get the meditation message now\n"
        "• /quote - Get a motivational quote\n"
        "• /status - Check your subscription status\n"
        "• /stop - Unsubscribe from reminders"
    )
    
    # Schedule daily reminder for this chat
    schedule_daily_reminder(context, chat_id)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command - unsubscribe user from daily reminders."""
    chat_id = update.effective_chat.id
    logger.info(f"User {chat_id} stopped the bot")
    
    # Remove any scheduled jobs for this chat
    job_name = f"meditation_{chat_id}"
    for job in context.job_queue.get_jobs_by_name(job_name):
        job.remove()
    
    await update.message.reply_text(
        "You've been unsubscribed from daily meditation reminders.\n"
        "Use /start to subscribe again."
    )


async def meditate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /meditate command - send meditation message immediately."""
    chat_id = update.effective_chat.id
    logger.info(f"User {chat_id} requested meditation message")
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=MEDITATION_MESSAGE
    )
    logger.info(f"Sent meditation message to user {chat_id}")


async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quote command - send a motivational quote."""
    chat_id = update.effective_chat.id
    logger.info(f"User {chat_id} requested a quote")
    
    import random
    quote = random.choice(QUOTES)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"💭 {quote}"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show subscription status."""
    chat_id = update.effective_chat.id
    job_name = f"meditation_{chat_id}"
    
    jobs = list(context.job_queue.get_jobs_by_name(job_name))
    
    if jobs:
        next_time = get_next_reminder_time()
        await update.message.reply_text(
            "✅ You're subscribed to daily meditation reminders!\n\n"
            f"⏰ Next reminder: {next_time}\n"
            "Type /stop to unsubscribe."
        )
    else:
        await update.message.reply_text(
            "❌ You're not subscribed to reminders.\n\n"
            "Type /start to subscribe."
        )


def schedule_daily_reminder(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Schedule the daily meditation reminder for a specific chat."""
    job_name = f"meditation_{chat_id}"
    
    # Remove existing job if any
    for job in context.job_queue.get_jobs_by_name(job_name):
        job.remove()
    
    # Schedule new daily job at 9:20 AM Berlin time
    context.job_queue.run_daily(
        send_meditation_reminder,
        time=time(9, 20),  # 9:20 AM
        days=tuple(range(7)),  # Every day
        name=job_name,
        chat_id=chat_id,
        timezone=BERLIN_TZ
    )
    logger.info(f"Scheduled daily reminder for user {chat_id} at 9:20 AM CET")


async def send_meditation_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send meditation reminder to the scheduled chat."""
    job = context.job
    chat_id = job.chat_id
    logger.info(f"Triggering daily meditation reminder for chat {chat_id}")
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=MEDITATION_MESSAGE
        )
        logger.info(f"Successfully sent meditation reminder to user {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send meditation reminder to user {chat_id}: {e}")


async def main():
    """Main function to run the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Use PicklePersistence to save job schedule across restarts
    persistence = PicklePersistence(filepath='bot_data.pkl')
    
    # Create Application with persistence
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).persistence(persistence).build()
    
    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('meditate', meditate))
    application.add_handler(CommandHandler('quote', quote))
    application.add_handler(CommandHandler('status', status))
    
    # Add error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)
    
    # Run the bot
    logger.info("Starting Telegram bot...")
    await application.run_polling()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    import asyncio
    asyncio.run(main())

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
from pytz import timezone
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

# Store custom reminder times for each user (chat_id -> {"hour": int, "minute": int})
user_reminder_times = {}

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
        "Your daily meditation reminder is set for 8:55 AM CET.\n\n"
        "📝 Commands:\n"
        "• /remind HH:MM - Set custom reminder time\n"
        "• /myremind - Check your reminder time\n"
        "• /defaultremind - Reset to default (8:55 AM)\n"
        "• /stop - Unsubscribe from reminders\n\n"
        "Example: /remind 09:30"
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
    """Send meditation reminder to all subscribed users at their custom times."""
    from datetime import datetime
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    
    for chat_id in subscribed_users:
        # Get user's custom time or use default (8:55 CET)
        if chat_id in user_reminder_times:
            target_hour = user_reminder_times[chat_id]["hour"]
            target_minute = user_reminder_times[chat_id]["minute"]
        else:
            target_hour = 8
            target_minute = 55
        
        # Send reminder if current time matches user's target time
        if current_hour == target_hour and current_minute == target_minute:
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text=MEDITATION_MESSAGE
                )
                logger.info(f"Sent meditation reminder to user {chat_id} at {target_hour:02d}:{target_minute:02d}")
            except Exception as e:
                logger.error(f"Failed to send message to user {chat_id}: {e}")
                # Remove invalid chat_id
                subscribed_users.discard(chat_id)


async def send_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a test message to verify the bot is working."""
    chat_id = update.effective_chat.id
    await update.message.reply_text("🧘 Test message: Your meditation reminder bot is working!")
    logger.info(f"Sent test message to user {chat_id}")


async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remind command - set custom reminder time.
    Usage: /remind HH:MM (e.g., /remind 09:30 or /remind 8:40)
    """
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text(
            "🕐 To set your reminder time, use:\n"
            "📝 /remind HH:MM\n\n"
            "Example: /remind 09:30\n"
            "or: /remind 8:40\n\n"
            "Use /myremind to see your current reminder time."
        )
        return
    
    try:
        time_arg = context.args[0]
        
        # Parse time (support both HH:MM and H:MM formats)
        if ':' in time_arg:
            parts = time_arg.split(':')
            hour = int(parts[0])
            minute = int(parts[1])
        else:
            # If no colon, assume it's just the hour
            hour = int(time_arg)
            minute = 0
        
        # Validate time
        if hour < 0 or hour > 23:
            await update.message.reply_text("❌ Hour must be between 0 and 23!")
            return
        if minute < 0 or minute > 59:
            await update.message.reply_text("❌ Minute must be between 0 and 59!")
            return
        
        # Store custom time
        user_reminder_times[chat_id] = {"hour": hour, "minute": minute}
        
        await update.message.reply_text(
            f"✅ Your meditation reminder is set for {hour:02d}:{minute:02d} daily!\n\n"
            "Use /myremind to check your time.\n"
            "Use /defaultremind to reset to default (8:55 AM)."
        )
        logger.info(f"User {chat_id} set reminder time to {hour:02d}:{minute:02d}")
        
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Invalid time format!\n"
            "Use: /remind HH:MM\n"
            "Example: /remind 09:30"
        )


async def my_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myremind command - show current reminder time."""
    chat_id = update.effective_chat.id
    
    if chat_id in user_reminder_times:
        hour = user_reminder_times[chat_id]["hour"]
        minute = user_reminder_times[chat_id]["minute"]
        await update.message.reply_text(
            f"🕐 Your meditation reminder is set for {hour:02d}:{minute:02d} daily!"
        )
    else:
        await update.message.reply_text(
            "🕐 Your reminder is set to the default time: 8:55 AM\n\n"
            "Use /remind HH:MM to set a custom time."
        )


async def default_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /defaultremind command - reset to default reminder time."""
    chat_id = update.effective_chat.id
    
    if chat_id in user_reminder_times:
        del user_reminder_times[chat_id]
    
    await update.message.reply_text(
        "✅ Your reminder has been reset to the default time: 8:55 AM\n\n"
        "Use /remind HH:MM to set a custom time."
    )
    logger.info(f"User {chat_id} reset to default reminder time")


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
    application.add_handler(CommandHandler('remind', set_reminder))
    application.add_handler(CommandHandler('myremind', my_reminder))
    application.add_handler(CommandHandler('defaultremind', default_reminder))

    # Create scheduler with Europe/Berlin timezone (CET/CEST)
    berlin_tz = timezone('Europe/Berlin')
    scheduler = AsyncIOScheduler(timezone=berlin_tz)

    # Schedule meditation reminder check every minute
    # Each user gets reminded at their custom time (or default 8:55 AM CET)
    scheduler.add_job(
        send_meditation_reminder,
        CronTrigger(minute='*', timezone=berlin_tz),  # Run every minute in Berlin time
        args=[application],
        id='meditation_reminder',
        name='Check and send meditation reminders'
    )

    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started - meditation reminders will be sent at each user's custom time (default 8:55 AM CET)")

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

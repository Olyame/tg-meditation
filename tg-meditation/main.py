"""
Simple Telegram Bot for Daily Meditation Reminders
Sends reminder every morning at 10:40 AM CET.
"""

import json
import os
from datetime import time
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from pytz import timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
USERS_FILE = 'users.json'
BERLIN_TZ = timezone('Europe/Berlin')

# Message
MESSAGE = """
🌅 Guten Morgen! 🌅

Time for your daily meditation.

🧘 Find a comfortable position
🌬️ Take deep breaths
💭 Clear your mind

Quiet the mind, and the soul will speak.

Enjoy your meditation! 🙏
I'm with u. O. <3
"""


def load_users():
    """Load subscribed users from file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_users(users):
    """Save subscribed users to file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe user to daily reminders."""
    chat_id = update.effective_chat.id
    
    users = load_users()
    if chat_id not in users:
        users.append(chat_id)
        save_users(users)
        await update.message.reply_text("✅ Subscribed to daily meditation reminders!")
    else:
        await update.message.reply_text("You're already subscribed!")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe user from daily reminders."""
    chat_id = update.effective_chat.id
    
    users = load_users()
    if chat_id in users:
        users.remove(chat_id)
        save_users(users)
        await update.message.reply_text("❌ Unsubscribed from daily reminders.")
    else:
        await update.message.reply_text("You're not subscribed.")


async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send test reminder immediately."""
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=MESSAGE)


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send reminder to all subscribed users."""
    users = load_users()
    for chat_id in users:
        try:
            await context.bot.send_message(chat_id=chat_id, text=MESSAGE)
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")


async def main():
    """Run the bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found!")
        return
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(CommandHandler('test', test))
    
    # Daily reminder at 10:40 AM Berlin time
    app.job_queue.run_daily(
        send_reminder,
        time=time(10, 40, tzinfo=BERLIN_TZ),
        timezone=BERLIN_TZ
    )
    
    print("Bot started! Press Ctrl+C to stop.")
    await app.run_polling()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

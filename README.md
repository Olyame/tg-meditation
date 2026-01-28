# Telegram Meditation Reminder Bot

A simple Telegram bot that sends daily meditation reminders at 8 AM.

## Features

- 📅 Daily meditation reminders at 8 AM
- 🧘 Customizable reminder messages
- 🔔 Subscribe/unsubscribe commands
- ✅ Test command to verify the bot is working

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` to create a new bot
3. Follow the instructions to name your bot
4. Copy the Bot Token (starts with `:`)

### 2. Configure the Bot

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and replace `your_bot_token_here` with your actual bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

```bash
python main.py
```

## Commands

- `/start` - Subscribe to daily meditation reminders
- `/stop` - Unsubscribe from reminders
- `/test` - Send a test message

## Customization

You can customize the meditation reminder message by editing the `MEDITATION_MESSAGE` variable in `main.py`.

## Requirements

- Python 3.8+
- python-telegram-bot==20.8
- APScheduler==3.10.4
- python-dotenv==1.0.1

## Notes

- The bot uses APScheduler to send reminders at 8 AM daily
- Reminders are sent to all users who have subscribed using `/start`
- The bot must be running for reminders to be sent

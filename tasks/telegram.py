import telegram

from app.config import Config


def send_telegram_message(message: str) -> bool:
    if not Config.TELEGRAM_TOKEN or not Config.TELEGRAM_CHAT_ID:
        return False

    bot = telegram.Bot(Config.TELEGRAM_TOKEN)

    bot.send_message(Config.TELEGRAM_CHAT_ID, message)

    return True

from telegram import Bot
from telegram.error import TelegramError
from .config import settings
from loguru import logger


class TelegramNotifier:
    def __init__(self):
        self.bot = Bot(token=settings.tg_bot_token)
        self.chat_id = settings.tg_chat_id

    def send_slots(self, new_slots: list[str]):
        if not new_slots:
            return
        text = "🎯 New lesson slots available:\n" + "\n".join(new_slots)
        text += "\n\nBook manually: [go to portal]"
        try:
            self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="Markdown")
            logger.info("Sent Telegram notification for %d new slots", len(new_slots))
        except TelegramError as e:
            logger.error("Failed to send Telegram message: %s", e)

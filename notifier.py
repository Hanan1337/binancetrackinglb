# notifier.py
import aiohttp
import logging

logger = logging.getLogger(__name__)

class Notifier:
    async def send_message(self, session: aiohttp.ClientSession, message: str, target: str = None):
        raise NotImplementedError("Subclasses must implement send_message")

class TelegramNotifier(Notifier):
    def __init__(self, bot_token, default_chat_id):
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id

    async def send_message(self, session: aiohttp.ClientSession, message: str, target: str = None):
        api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        chat_id = target or self.default_chat_id
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'html',
            'disable_web_page_preview': True
        }
        logger.debug(f"Payload untuk Telegram: {payload}")
        try:
            async with session.post(api_url, json=payload) as response:
                response.raise_for_status()
                logger.info(f"Pesan berhasil dikirim ke chat {chat_id}")
                return True
        except aiohttp.ClientError as e:
            logger.error(f"Gagal mengirim pesan ke chat {chat_id}: {e}", exc_info=True)
            return False
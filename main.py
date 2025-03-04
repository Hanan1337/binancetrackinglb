# main.py
import asyncio
import logging
import time
import datetime
import aiohttp
import configparser
from message import telegram_polling, load_user_addresses, telegram_chat_id
from binance import get_other_leaderboard_base_info
from shared import TARGETED_USER_ADDRESSES, user_addresses_lock, USER_NICKNAMES
from position_tracker import PositionTracker
from notifier import TelegramNotifier

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
POLLING_INTERVAL = int(config['general']['polling_interval'])
ACCOUNT_INFO_URL_TEMPLATE = config['general']['account_info_url_template']
MESSAGE_TEMPLATES = {
    'new_position': config['telegram_messages']['new_position_template'],
    'closed_position': config['telegram_messages']['closed_position_template'],
    'current_positions': config['telegram_messages']['current_positions_template']
}

logger.info("Memulai inisialisasi TARGETED_USER_ADDRESSES")
TARGETED_USER_ADDRESSES.extend(load_user_addresses())
logger.debug(f"TARGETED_USER_ADDRESSES setelah inisialisasi: {TARGETED_USER_ADDRESSES}")

async def fetch_nicknames(session: aiohttp.ClientSession, force_refresh=False):
    logger.info("Memulai pengambilan nickname untuk semua encryptedUid")
    with user_addresses_lock:
        for encrypted_uid in TARGETED_USER_ADDRESSES:
            if force_refresh or encrypted_uid not in USER_NICKNAMES:
                logger.debug(f"Mengambil nickname untuk encryptedUid: {encrypted_uid}")
                base_info = await get_other_leaderboard_base_info(session, encrypted_uid)
                if isinstance(base_info, dict):
                    USER_NICKNAMES[encrypted_uid] = base_info.get("nickName", encrypted_uid)
                    logger.debug(f"Nickname untuk {encrypted_uid}: {USER_NICKNAMES[encrypted_uid]}")
                else:
                    USER_NICKNAMES[encrypted_uid] = encrypted_uid
                    logger.warning(f"Gagal mengambil nickname untuk {encrypted_uid}, menggunakan encryptedUid sebagai fallback")
    logger.info(f"Nickname yang berhasil diambil: {USER_NICKNAMES}")

async def monitor_positions():
    tracker = PositionTracker(ACCOUNT_INFO_URL_TEMPLATE)
    notifier = TelegramNotifier(config['telegram']['bottoken'], telegram_chat_id)
    async with aiohttp.ClientSession() as session:
        logger.info("Memulai pemantauan posisi Binance Leaderboard")
        await fetch_nicknames(session)
        
        while True:
            try:
                start_time = time.time()
                logger.debug("Memulai iterasi pemantauan posisi")
                
                with user_addresses_lock:
                    current_addresses = TARGETED_USER_ADDRESSES.copy()
                logger.debug(f"Daftar encryptedUid yang dipantau: {current_addresses}")

                # Panggil track_positions dengan argumen yang sesuai
                await tracker.track_positions(session, current_addresses, notifier, MESSAGE_TEMPLATES, USER_NICKNAMES)

                ping_time = (time.time() - start_time) * 1000
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"✅ Bot is still running | Time: {current_time} | Ping: {ping_time:.2f}ms")
                await asyncio.sleep(POLLING_INTERVAL)
            
            except Exception as e:
                logger.error(f"Global error occurred: {e}", exc_info=True)
                error_message = f"Global error occurred:\n{e}\n\nRetrying after {POLLING_INTERVAL}s"
                await notifier.send_message(session, error_message)
                await asyncio.sleep(POLLING_INTERVAL)

async def main():
    logger.info("Memulai eksekusi utama bot Binance Leaderboard Tracker")
    await asyncio.gather(
        telegram_polling(),
        monitor_positions()
    )
    logger.info("Eksekusi utama selesai")

if __name__ == "__main__":
    logger.info("Menjalankan bot Binance Leaderboard Tracker")
    asyncio.run(main())
# setup.py
import json
import configparser
import logging

logger = logging.getLogger(__name__)

def setup():
    logger.info("Memulai proses setup konfigurasi bot")
    
    config = configparser.ConfigParser()
    config['telegram'] = {}
    config['general'] = {}
    config['telegram_messages'] = {}
    
    while True:
        bottoken = input("Masukkan token bot Telegram: ").strip()
        if bottoken and ":" in bottoken:
            break
        print("Token bot harus mengandung ':' dan tidak boleh kosong.")
        logger.warning("Input token bot tidak valid")

    while True:
        chatid = input("Masukkan chat ID Telegram: ").strip()
        if chatid and chatid.lstrip('-').isdigit():
            break
        print("Chat ID harus berupa angka (bisa negatif) dan tidak boleh kosong.")
        logger.warning("Input chat ID tidak valid")

    while True:
        admins_input = input("Daftar admin (contoh: -123456789,123456): ").strip()
        try:
            admins = [int(admin.strip()) for admin in admins_input.split(',') if admin.strip()]
            if admins:
                break
            print("Daftar admin tidak boleh kosong.")
        except ValueError:
            print("Setiap ID harus berupa angka (bisa negatif).")
        logger.warning("Input daftar admin tidak valid")

    polling_interval = input("Masukkan interval polling (detik, default 60): ").strip() or "60"
    
    config['telegram']['bottoken'] = bottoken
    config['telegram']['chatid'] = chatid
    config['telegram']['admins'] = ','.join(map(str, admins))
    config['general']['polling_interval'] = polling_interval
    config['general']['account_info_url_template'] = "https://www.binance.com/en/futures-activity/leaderboard/user/um?encryptedUid={}"
    config['telegram_messages']['new_position_template'] = "⚠️ <u>【<b>{nickName}</b>】</u>\n❇️ New position opened\n\n<b>Position: {symbol} {estimated_position} {leverage}X</b>\n\n💵 Base currency - USDT\n━━━━━━━━━━━━━━━━━━\n🎯 <b>Entry Price:</b> {entry_price}\n💰 <b>Est. Entry Size:</b> {position_value}\n{pnl_emoji} <b>PnL:</b> {pnl}\n\n<b>Last Update:</b>\n{updatetime} (UTC+7)\n<b><a href='{profile_url}'>VIEW PROFILE ON BINANCE</a></b>"
    config['telegram_messages']['closed_position_template'] = "⚠️ <u>【<b>{nickName}</b>】</u>\n⛔️ Position closed\n\n<b>Position: {symbol} {estimated_position} {leverage}X</b>\n\n💵 <b>Current Price:</b> {current_price} USDT\n\n<b>Last Update:</b>\n{updatetime} (UTC+7)\n<b><a href='{profile_url}'>VIEW PROFILE ON BINANCE</a></b>"
    config['telegram_messages']['current_positions_template'] = "⚠️ <u>【<b>{nickName}</b>】</u>\n💎 Current positions:\n\n{positions}\n\n<b>Last Update:</b>\n{updatetime} (UTC+7)\n<b><a href='{profile_url}'>VIEW PROFILE ON BINANCE</a></b>"

    try:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        logger.info("File config.ini telah dibuat")
    except IOError as e:
        logger.error(f"Gagal menulis config.ini: {e}", exc_info=True)
        raise

    user_addresses = []
    print("\nMasukkan encryptedUid pengguna (tekan Enter setelah setiap UID, kosongkan untuk selesai):")
    while True:
        uid = input("Encrypted UID: ").strip()
        if not uid:
            break
        if len(uid) >= 32 and uid.isalnum():
            user_addresses.append(uid)
        else:
            print("Encrypted UID harus alfanumerik dan minimal 32 karakter.")
            logger.warning(f"Encrypted UID tidak valid: {uid}")
    
    try:
        with open('user_addresses.json', 'w') as f:
            json.dump(user_addresses, f, indent=2)
        logger.info(f"File user_addresses.json telah dibuat dengan {len(user_addresses)} UID")
    except IOError as e:
        logger.error(f"Gagal menulis user_addresses.json: {e}", exc_info=True)
        raise

    print("\nSetup selesai! File config.ini dan user_addresses.json telah dibuat.")
    logger.info("Proses setup selesai")

if __name__ == "__main__":
    logger.info("Menjalankan setup.py")
    setup()
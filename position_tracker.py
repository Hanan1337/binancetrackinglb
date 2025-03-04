# position_tracker.py
import pandas as pd
import logging
import asyncio
from binance import get_other_position, get_markprice
from constants import PositionType, Emoji

logger = logging.getLogger(__name__)

class PositionTracker:
    def __init__(self, account_info_url_template):
        self.previous_symbols = {}
        self.previous_position_results = {}
        self.is_first_runs = {}
        self.account_info_url_template = account_info_url_template

    def _modify_data(self, data) -> pd.DataFrame:
        logger.debug(f"Memproses data untuk DataFrame: {data}")
        if not data or 'positions' not in data:
            logger.warning("Struktur data tidak valid atau 'positions' tidak ada dalam data.")
            return pd.DataFrame()

        positions = data['positions']
        df = pd.DataFrame(positions)
        logger.debug(f"DataFrame awal: {df.head()}")

        required_columns = ['coin', 'size', 'entry_price', 'position_value', 'unrealized_pnl', 'leverage', 'updateTime']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logger.error(f"Kolom yang diperlukan hilang: {missing_cols}")
            return pd.DataFrame()

        df.set_index('coin', inplace=True)
        df['estimatedPosition'] = df['size'].apply(lambda x: PositionType.LONG.value if x > 0 else PositionType.SHORT.value)
        logger.debug(f"DataFrame setelah pemrosesan: {df.head()}")
        return df[['estimatedPosition', 'leverage', 'entry_price', 'position_value', 'unrealized_pnl', 'updateTime']]

    async def track_positions(self, session, encrypted_uids, notifier, message_templates, user_nicknames):
        tasks = [get_other_position(session, uid) for uid in encrypted_uids]
        position_infos = await asyncio.gather(*tasks, return_exceptions=True)

        notification_tasks = []
        for uid, info in zip(encrypted_uids, position_infos):
            if isinstance(info, str):
                notification_tasks.append(notifier.send_message(session, f"Error untuk {uid}: {info}"))
                continue

            result = self._modify_data(info)

            if self.is_first_runs.get(uid, True):
                logger.debug(f"Mengirim posisi saat ini untuk iterasi pertama {uid}")
                notification_tasks.append(self._notify_current_positions(session, result, uid, notifier, message_templates['current_positions'], user_nicknames))
            else:
                new_symbols = result.index.difference(self.previous_symbols.get(uid, pd.Index([])))
                if not new_symbols.empty:
                    logger.debug(f"Posisi baru terdeteksi untuk {uid}: {new_symbols}")
                    for symbol in new_symbols:
                        notification_tasks.append(self._notify_new_position(session, symbol, result.loc[symbol], uid, notifier, message_templates['new_position'], user_nicknames))

                closed_symbols = self.previous_symbols.get(uid, pd.Index([])).difference(result.index)
                if not closed_symbols.empty:
                    logger.debug(f"Posisi tertutup terdeteksi untuk {uid}: {closed_symbols}")
                    for symbol in closed_symbols:
                        if symbol in self.previous_position_results.get(uid, pd.DataFrame()).index:
                            notification_tasks.append(self._notify_closed_position(session, symbol, self.previous_position_results[uid].loc[symbol], uid, notifier, message_templates['closed_position'], user_nicknames))

            self.previous_position_results[uid] = result.copy()
            self.previous_symbols[uid] = result.index.copy()
            self.is_first_runs[uid] = False

        if notification_tasks:
            logger.debug(f"Menjalankan {len(notification_tasks)} tugas pengiriman pesan paralel")
            await asyncio.gather(*notification_tasks)

        expired_uids = set(self.previous_position_results.keys()) - set(encrypted_uids)
        for uid in expired_uids:
            self.previous_position_results.pop(uid, None)
            self.previous_symbols.pop(uid, None)
            self.is_first_runs.pop(uid, None)
            logger.debug(f"Membersihkan cache untuk UID yang tidak dipantau: {uid}")

    async def _notify_new_position(self, session, symbol, row, encrypted_uid, notifier, template, user_nicknames):
        nickName = user_nicknames.get(encrypted_uid, encrypted_uid)
        pnl_emoji = Emoji.PROFIT if row['unrealized_pnl'] >= 0 else Emoji.LOSS
        entry_size = f"{row['position_value']:.5f}"  # Batasi 5 desimal
        message = template.format(
            nickName=nickName, symbol=symbol, estimated_position=row['estimatedPosition'],
            leverage=row['leverage'], entry_price=row['entry_price'],
            position_value=entry_size, pnl=row['unrealized_pnl'],
            pnl_emoji=pnl_emoji, updatetime=row['updateTime'],
            profile_url=self.account_info_url_template.format(encrypted_uid)
        )
        await notifier.send_message(session, message)

    async def _notify_closed_position(self, session, symbol, row, encrypted_uid, notifier, template, user_nicknames):
        nickName = user_nicknames.get(encrypted_uid, encrypted_uid)
        current_price = await get_markprice(session, symbol)
        entry_size = f"{row['position_value']:.5f}"  # Batasi 5 desimal
        message = template.format(
            nickName=nickName, symbol=symbol, estimated_position=row['estimatedPosition'],
            leverage=row['leverage'], current_price=current_price,
            position_value=entry_size, updatetime=row['updateTime'],
            profile_url=self.account_info_url_template.format(encrypted_uid)
        )
        await notifier.send_message(session, message)

    async def _notify_current_positions(self, session, position_result, encrypted_uid, notifier, template, user_nicknames):
        nickName = user_nicknames.get(encrypted_uid, encrypted_uid)
        
        if position_result.empty:
            message = f"⚠️ <u>【<b>{nickName}</b>】</u>\n💎 <b>No positions found</b>"
            await notifier.send_message(session, message)
        else:
            for symbol, row in position_result.iterrows():
                pnl_emoji = Emoji.PROFIT if row['unrealized_pnl'] >= 0 else Emoji.LOSS
                entry_size = f"{row['position_value']:.5f}"  # Batasi 5 desimal
                message = (
                    f"⚠️ <u>【<b>{nickName}</b>】</u>\n"
                    f"💎 Current positions:\n\n"
                    f"<b>Position: {symbol} {row['estimatedPosition']} {row['leverage']}X</b>\n\n"
                    f"Base currency - USDT\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🎯 <b>Entry Price:</b> {row['entry_price']}\n"
                    f"💰 <b>Est. Entry Size:</b> {entry_size}\n"
                    f"{pnl_emoji} <b>PnL:</b> {row['unrealized_pnl']}\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"<b>Last Update:</b>\n"
                    f"{row['updateTime']} (UTC+7)\n"
                    f"<b><a href='{self.account_info_url_template.format(encrypted_uid)}'>VIEW PROFILE ON BINANCE</a></b>"
                )
                await notifier.send_message(session, message)
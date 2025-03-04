# shared.py
import threading
import logging

logger = logging.getLogger(__name__)

logger.info("Inisialisasi variabel global di shared.py")
TARGETED_USER_ADDRESSES = []
user_addresses_lock = threading.Lock()
USER_NICKNAMES = {}
logger.debug(f"TARGETED_USER_ADDRESSES awal: {TARGETED_USER_ADDRESSES}")
logger.debug(f"USER_NICKNAMES awal: {USER_NICKNAMES}")
logger.debug("Lock threading untuk user_addresses_lock telah dibuat")
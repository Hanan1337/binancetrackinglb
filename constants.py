# constants.py
from enum import Enum

class PositionType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class Emoji:
    PROFIT = "🟢"
    LOSS = "🔴"
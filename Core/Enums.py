from enum import Enum

class StrategyState(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    PAUSE = "PAUSE"

class CandleInterval(Enum):
    min = "1minute"
    three_min = "3minute"
    five_min = "5minute"
    ten_min = "10minute"
    fifteen_min = "15minute"
    thirty_min = "30minute"
    hourly = "60minute"
    day = "day"

class TradeIdentifier(Enum):
    ENTRY = "entry"
    SQUARE_OFF = "square_off"
    STOP_SQUARE_OFF = "stop_square_off"
    STOP_LOSS_TRIGGERED = "stop_loss_triggered"
    TARGET_TRIGGERED = "target_triggered"
    DAY_END_SQUARE_OFF = "day_end_square_off"

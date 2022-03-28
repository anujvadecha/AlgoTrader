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

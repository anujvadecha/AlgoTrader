import logging

from Indicators.indicator_base import Indicator
LOGGER = logging.getLogger(__name__)

class AverageTrueRange(Indicator):
    def __init__(self, instrument, timeframe, length):
        self.length = length

        # indicator calculated values
        self.tr_rma = 0.00
        self.ATR = 0.00
        self.previous_close = 0.00

        super().__init__(instrument=instrument, timeframe=timeframe)

    def calculate(self, candle=None):
        if self.last_candle["date"] == candle["date"]:
            return
        self.last_candle = candle

        tr1 = candle["high"] - candle["low"]
        tr2 = abs(candle["high"] - self.previous_close)
        tr3 = abs(candle["low"] - self.previous_close)
        tr = tr1
        if self.previous_close != 0.00:
            tr = max(tr1, tr2, tr3)
        alpha = float(1.0 / self.length)
        self.tr_rma = (alpha * tr) + (1 - alpha) * self.tr_rma
        self.ATR = round(self.tr_rma, 4)
        self.previous_close = candle["close"]
        self.last_candle = candle
        LOGGER.debug("atr excution over")

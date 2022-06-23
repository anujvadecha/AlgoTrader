from Indicators.indicator_base import Indicator
import logging
LOGGER = logging.getLogger(__name__)


class SuperTrend(Indicator):

    def __init__(self, instrument, timeframe, atr_length=10, factor=3):
        self.atr_length = atr_length
        self.factor = factor

        # indicator calculated values
        self.tr_list = []
        self.tr_rma = 0.00
        self.atr = 0.00
        self.previous_close = 0.00
        self.upper_band = 0
        self.lower_band = 0
        self.supertrend = 0
        self.trend = 0

        super().__init__(instrument=instrument, timeframe=timeframe)
        LOGGER.debug(f"st execution over st value {self.supertrend} trend{self.trend}")

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
        if len(self.tr_list) == self.atr_length:
            self.tr_list = self.tr_list[1:]
        self.tr_list.append(tr)
        self.atr = round(sum(self.tr_list) / len(self.tr_list), 3)

        hla = (candle["high"] + candle["low"]) / 2.0
        upper_basic = hla + (self.factor * self.atr)
        lower_basic = hla - (self.factor * self.atr)

        upper_band_final = self.upper_band
        lower_band_final = self.lower_band

        if upper_basic < self.upper_band or self.previous_close > self.upper_band:
            upper_band_final = upper_basic

        if lower_basic > self.lower_band or self.previous_close < self.lower_band:
            lower_band_final = lower_basic

        if self.supertrend == self.upper_band:
            if candle["close"] > upper_band_final:
                self.supertrend = lower_band_final
                self.trend = 1
            elif candle["close"] < upper_band_final:
                self.supertrend = upper_band_final
        elif self.supertrend == self.lower_band:
            if candle["close"] > lower_band_final:
                self.supertrend = lower_band_final
            elif candle["close"] < lower_band_final:
                self.supertrend = upper_band_final
                self.trend = -1

        self.upper_band = upper_band_final
        self.lower_band = lower_band_final
        self.previous_close = candle["close"]

from Indicators.indicator_base import Indicator


class ParabolicSAR(Indicator):
    def __init__(self, instrument, timeframe, start=0.02, increment_step=0.02, inc_max=0.2):
        self.start = start
        self.increment_step = increment_step
        self.inc_max = inc_max

        # indicator calculated values
        self.ep = None
        self.trend = 0
        self.af = 0.00
        self.PSAR = float('nan')
        self.prev_candle = None
        self.prev_PSAR = 0.00

        super().__init__(instrument=instrument, timeframe=timeframe)

    def calculate(self, candle=None):
        # starting the psar
        if self.trend == 0:
            self.trend = 1
            self.PSAR = candle["low"]
            self.af = self.start
            self.ep = candle["high"]
        else:
            if self.trend > 0:
                # bullish trend calculations
                self.PSAR = self.PSAR + (self.af * (self.ep - self.PSAR))
                # check for reversal
                if candle["low"] <= self.prev_PSAR:
                    self.trend = -1
                    self.PSAR = self.ep
                    self.af = self.start
                    self.ep = candle["low"]
                else:
                    if candle["high"] > self.ep:
                        self.ep = candle["high"]
                        self.af = min(self.af + self.increment_step, self.inc_max)
                        self.PSAR = self.prev_PSAR + (self.af * (self.ep - self.prev_PSAR))
                    if candle["low"] < self.PSAR:
                        self.PSAR = candle["low"]
            else:
                # bearish trend calculations
                self.PSAR = self.PSAR - (self.af * (self.PSAR - self.ep))
                # check for reversal
                if candle["high"] >= self.prev_PSAR:
                    self.trend = 1
                    self.PSAR = self.ep
                    self.af = self.start
                    self.ep = candle["high"]
                else:
                    if candle["low"] < self.ep:
                        self.ep = candle["low"]
                        self.af = min(self.af + self.increment_step, self.inc_max)
                        self.PSAR = self.prev_PSAR - (self.af * (self.prev_PSAR - self.ep))
                    if candle["high"] > self.PSAR:
                        self.PSAR = candle["high"]
        self.prev_candle = candle.copy()
        self.PSAR = round(self.PSAR, 4)
        self.prev_PSAR = self.PSAR

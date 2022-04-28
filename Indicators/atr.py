from datetime import datetime

import pandas as pd

from Indicators.indicator_base import Indicator


class AverageTrueRange(Indicator):
    def __init__(self, instrument, interval, length):
        self.instrument = instrument
        self.interval = interval
        self.length = length
        self.init_time = datetime.now().replace(hour=9, minute=15)

        # indicator calculated values
        self.tr_rma = 0.00
        self.ATR = 0.00
        self.previous_close = 0.00

        super().__init__()

    def calculate(self):
        hist_data = self.datamanager.get_historical_data(instrument=self.instrument,
                                                         from_date=self.init_time,
                                                         interval=self.interval)
        hist_df = pd.DataFrame(hist_data)
        candle = hist_df.iloc[-1]
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

from datetime import datetime

import pandas as pd

from Indicators.indicator_base import Indicator


class AverageTrueRange(Indicator):
    def __init__(self,instrument, interval, k_length=14, k_smooth=1, d_smooth=3):
        self.instrument = instrument
        self.interval = interval
        self.k_length = k_length
        self.k_smooth = k_smooth
        self.d_smooth = d_smooth
        self.init_time = datetime.now().replace(hour=9, minute=15)

        # indicator calculated values
        self.high_list = []
        self.low_list = []
        self.k_list = []
        self.k_value = float('nan')
        self.d_list = []
        self.d_value = float('nan')
        self.signal = None

        super().__init__()

    def calculate(self):
        hist_data = self.datamanager.get_historical_data(instrument=self.instrument,
                                                         from_date=self.init_time,
                                                         interval=self.interval)
        hist_df = pd.DataFrame(hist_data)
        candle = hist_df.iloc[-1]
        if len(self.high_list) > self.k_length:
            self.high_list = self.high_list[1:]
        self.high_list.append(candle["high"])
        highest = max(self.high_list)

        if len(self.low_list) > self.k_length:
            self.low_list = self.low_list[1:]
        self.low_list.append(candle["low"])
        lowest = min(self.low_list)

        if highest - lowest <= 0:
            return

        k = (candle["close"] - lowest) / (highest - lowest) * 100
        if len(self.k_list) > self.k_smooth:
            self.k_list = self.k_list[1:]
        self.k_list.append(k)

        k = round(sum(self.k_list) / len(self.k_list), 3)
        if len(self.d_list) > self.d_smooth:
            self.d_list = self.d_list[1:]
        self.d_list.append(k)

        d = round(sum(self.d_list) / len(self.d_list), 3)

        signal = "nu"
        if k > 80 or d > 80:
            signal = "ob"
        elif k < 20 or d < 20:
            signal = "os"

        self.k_value = k
        self.d_value = d
        self.signal = signal


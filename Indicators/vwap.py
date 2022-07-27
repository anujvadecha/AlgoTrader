from datetime import datetime

from Indicators.indicator_base import Indicator


class VolumeWeightedAveragePrice(Indicator):
    def __init__(self, instrument, interval):
        self.instrument = instrument
        self.interval = interval
        self.init_time = datetime.now().replace(hour=9, minute=15)
        self.vwap_value = None
        self.volume_sum = None
        self.price_volume_sum = None
        super().__init__(instrument=instrument, timeframe=interval)

    def calculate(self, candle=None):
        if self.last_candle["date"] == candle["date"]:
            return
        self.last_candle = candle
        if candle["date"].hour == 9 and candle["date"].minute == 15:
            self.vwap_value = (candle["close"] + candle["high"] + candle["low"]) / 3
            self.volume_sum = candle["volume"]
            self.price_volume_sum = self.vwap_value * candle["volume"]
            print(
                f"VWAP price for {self.last_candle['date']} is {self.vwap_value} volume sum {self.volume_sum} price volume sum {self.price_volume_sum} candle {self.last_candle}")
            return
        if self.vwap_value == None:
            return
        if self.vwap_value:
            self.volume_sum = self.volume_sum + candle["volume"]
            price = (candle["close"] + candle["high"] + candle["low"]) / 3
            self.price_volume_sum = self.price_volume_sum + price * candle["volume"]
            self.vwap_value = self.price_volume_sum / self.volume_sum
        print(f"VWAP price for {self.last_candle['date']} is {self.vwap_value} volume sum {self.volume_sum} price volume sum {self.price_volume_sum} candle {self.last_candle}")

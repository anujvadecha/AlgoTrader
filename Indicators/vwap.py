from datetime import datetime

from Indicators.indicator_base import Indicator


class VolumeWeightedAveragePrice(Indicator):
    def __init__(self, instrument, interval):
        self.instrument = instrument
        self.interval = interval
        self.init_time = datetime.now().replace(hour=9,minute=15)
        super().__init__()

    def calculate(self):
        hist_data = self.datamanager.get_historical_data(instrument=self.instrument,
                                                         from_date=self.init_time,
                                                         interval=self.interval)

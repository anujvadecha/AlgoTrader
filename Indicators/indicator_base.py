import datetime

from Managers.MarketDataManager import MarketDataManager
from MessageClasses import Messages
from datetime import datetime, timedelta


class Indicator:
    """
    base indicator class
    """
    def __init__(self, timeframe, instrument):
        self.datamanager = MarketDataManager.get_instance()
        self.message = Messages.getInstance()
        self.timeframe = timeframe
        self.instrument = instrument
        self.last_candle = {"date":None}
        now = datetime.now()
        historical_data = self.datamanager.get_historical_data(instrument=self.instrument,
                                                               interval=timeframe,
                                                               from_date=now - timedelta(days=7),
                                                               to_date=now)

        for candle in historical_data:
            self.calculate(candle)

    def calculate(self, candle=None):
        """
        placeholder for calculation logic
        """
        pass

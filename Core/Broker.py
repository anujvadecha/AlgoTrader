from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Models.Models import Instrument


class Broker():

    def push_instrument(self,instrument:Instrument):
        InstrumentManager.get_instance().add_instrument(instrument)

    def push_L1_data(self,data):
        MarketDataManager.get_instance().push_level1_data(data)

    def push_L2_data(self,data):
        MarketDataManager.get_instance().updateL2Data(data)

    def subscribe(self,instrument):
        raise NotImplementedError

    def on_connect(self):
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def get_orders(self):
        raise NotImplementedError

    def get_trades(self):
        raise NotImplementedError

    def get_positions(self):
        raise NotImplementedError

    def get_holdings(self):
        raise NotImplementedError

    def get_historical_data(self,instrument,from_date,to_date,interval):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

    def load_instruments(self):
        raise NotImplementedError

    def get_connection_object(self):
        raise NotImplementedError

    def place_market_order(self, instrument, side, quantity, type):
        raise NotImplementedError

    def place_limit_order(self, instrument, side, quantity, type, price):
        raise NotImplementedError

if __name__=="main":
    Broker()

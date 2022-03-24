from queue import Queue

from Models.Models import Instrument, Tick
import threading
import time

class MarketDataManager():
    market_data_map = {}
    subscribed_callbacks = {}

    def get_historical_data(self,instrument,from_date, to_date, interval):
        # TODO Write logic to cache data and only call for what is required
        # TODO Write logic for live candle maker (Priority low)
        return self.data_broker.get_historical_data(instrument=instrument, from_date=from_date, to_date=to_date, interval=interval)

    def subscribe(self,instrument:Instrument,tick_callback=None):
        self.market_data_map[instrument.tradingsymbol] = Queue(maxsize=200)
        self.data_broker.subscribe(instrument)
        if tick_callback is not None:
            if instrument.tradingsymbol in self.subscribed_callbacks.keys():
                self.subscribed_callbacks[instrument.tradingsymbol].append(tick_callback)
            else:
                self.subscribed_callbacks[instrument.tradingsymbol] = []
                self.subscribed_callbacks[instrument.tradingsymbol].append(tick_callback)

    def push_level1_data(self,tick):
        if not tick.symbol in self.market_data_map.keys():
            self.market_data_map[tick.symbol] = Queue(maxsize=200)
        self.market_data_map[tick.symbol].put(tick)
    __instance = None

    @staticmethod
    def get_instance():
        if MarketDataManager.__instance == None:
            MarketDataManager()
        return MarketDataManager.__instance

    def __process_ticks_thread_funct(self):
        while True:
            for key in self.market_data_map.keys():
                if(self.market_data_map[key]!=None):
                    while not self.market_data_map[key].empty():
                        tick=self.market_data_map[key].get()
                        for callback in self.subscribed_callbacks[tick.symbol]:
                            callback(tick)
            time.sleep(0.1)

    def __init__(self):
        if MarketDataManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MarketDataManager.__instance = self
        t = threading.Thread(target=self.__process_ticks_thread_funct)
        t.start()
        from Managers.BrokerManager import BrokerManager
        self.data_broker = BrokerManager.get_instance().get_data_broker()



if __name__=="__main__":
    MarketDataManager.get_instance()

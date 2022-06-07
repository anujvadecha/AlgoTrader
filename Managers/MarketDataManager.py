from queue import Queue

from Core.Enums import CandleInterval
from Models.Models import Instrument, Tick
import threading
import time


class MarketDataManager():
    _market_data_map = {}
    _subscribed_callbacks = {}
    _subscribed_candle = {}

    def get_historical_data(self, instrument, from_date, to_date, interval: CandleInterval, continuous=False):
        # TODO Write logic to cache data and only call for what is required
        # TODO Write logic for live candle maker (Priority low)
        return self.data_broker.get_historical_data(instrument=instrument, from_date=from_date, to_date=to_date,
                                                    interval=interval.value)

    def _update_candle_subscription_data(self, instrument, interval, data):
        if len(data) <= 0: return
        already_existing_data = self._subscribed_candle[instrument.tradingsymbol][interval]["data"]
        if len(already_existing_data) > 0 :
            if already_existing_data[-1]["date"] >= data[0]["date"]:
                index = 0
                while (already_existing_data[-1]["date"] >= data[0]["date"]):
                    index = index + 1
                already_existing_data[instrument.tradingsymbol][interval]["data"].extend(data[index:])
            elif already_existing_data[-1]["date"] < data[0]["date"]:
                self._subscribed_candle[instrument.tradingsymbol][interval]["data"].extend(data)
        else:
            self._subscribed_candle[instrument.tradingsymbol][interval]["data"].extend(data)

    def subscribe_candle(self, instrument, interval, callback, initial_from_date, initial_to_date):
        if not self._subscribed_candle.get(instrument.tradingsymbol):
            self._subscribed_candle[instrument.tradingsymbol] = {}
        if not self._subscribed_candle[instrument.tradingsymbol].get(interval):
            self._subscribed_candle[instrument.tradingsymbol][interval] = {"data": [], "callbacks": [callback]}
        else:
            self._subscribed_candle[instrument.tradingsymbol][interval]["callbacks"].append(callback)
        data = self.get_historical_data(instrument=instrument, from_date=initial_from_date,
                                                    to_date=initial_to_date,
                                                    interval=interval)
        self._update_candle_subscription_data(instrument, interval, data)
        return self._subscribed_candle[instrument.tradingsymbol][interval]["data"]

    def subscribe(self, instrument: Instrument, tick_callback=None):
        self._market_data_map[instrument.tradingsymbol] = Queue(maxsize=200)
        self.data_broker.subscribe(instrument)
        if tick_callback is not None:
            if instrument.tradingsymbol in self._subscribed_callbacks.keys():
                self._subscribed_callbacks[instrument.tradingsymbol].append(tick_callback)
            else:
                self._subscribed_callbacks[instrument.tradingsymbol] = []
                self._subscribed_callbacks[instrument.tradingsymbol].append(tick_callback)

    def push_level1_data(self, tick):
        if not tick.symbol in self._market_data_map.keys():
            self._market_data_map[tick.symbol] = Queue(maxsize=200)
        self._market_data_map[tick.symbol].put(tick)

    __instance = None

    @staticmethod
    def get_instance():
        if MarketDataManager.__instance == None:
            MarketDataManager()
        return MarketDataManager.__instance

    def __process_ticks_thread_funct(self):
        while True:
            for key in self._market_data_map.keys():
                if (self._market_data_map[key] != None):
                    while not self._market_data_map[key].empty():
                        tick = self._market_data_map[key].get()
                        for callback in self._subscribed_callbacks[tick.symbol]:
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


if __name__ == "__main__":
    MarketDataManager.get_instance()


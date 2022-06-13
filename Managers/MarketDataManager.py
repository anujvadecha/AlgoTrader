import logging
import threading
import time
from datetime import timedelta, datetime
from queue import Queue

from pytimeparse.timeparse import timeparse

from Core.Enums import CandleInterval
from Core.Utils import get_candle_time_series_for_date_range
from Models.Models import Instrument

LOGGER = logging.getLogger(__name__)

class MarketDataManager():
    _market_data_map = {}
    _subscribed_callbacks = {}
    _subscribed_candle = {}
    _historical_data_cache = {}
    _historical_data_cache_v1 = {}

    def ceil_dt(self, dt, delta):
        return dt + (datetime.min - dt) % delta

    def _get_candle_time_series_for_date_range(self, from_date, to_date, interval: CandleInterval):
        import pandas as pd
        from_date = self.ceil_dt(from_date, timedelta(seconds=timeparse(interval.value)))
        range = pd.date_range(from_date, to_date, freq=interval.value)
        return list(range)

    def get_historical_data(self, instrument, from_date, to_date, interval: CandleInterval, continuous=False):
        # TODO Write logic to cache data and only call for what is required
        # TODO Write logic for live candle maker (Priority low)
        # _historical_data_cache_v1 = {
        # "NIFTY 50": {
        #                 "15min": [{"date":"", "open": "" }]
        #               }
        # }
        print(f"Interval {interval} timeparsed {timeparse(interval.value)}")
        time_series = get_candle_time_series_for_date_range(from_date, to_date, interval)
        if not self._historical_data_cache_v1.get(instrument.tradingsymbol, None):
            self._historical_data_cache_v1[instrument.tradingsymbol] = {interval: {}}
            LOGGER.info(f"Historical data cache initialized fresh {self._historical_data_cache_v1}")
        if not self._historical_data_cache_v1.get(instrument.tradingsymbol).get(interval):
            self._historical_data_cache_v1[instrument.tradingsymbol][interval] = {}
            LOGGER.info(f"Historical data cache initialized for new interval {self._historical_data_cache_v1}")
        if len(time_series) > 0 :
            # If data present in cache returning same data
            last_candle_expected = time_series[-1]
            first_candle_expected = time_series[0]
            first_candle_exists = self._historical_data_cache_v1[instrument.tradingsymbol][interval].get(first_candle_expected, None)
            last_candle_exists = self._historical_data_cache_v1[instrument.tradingsymbol][interval].get(last_candle_expected, None)
            if first_candle_exists and last_candle_exists:
                LOGGER.info(f"First and last candle exist hence returning cached data for {from_date} {to_date} {interval} {instrument.tradingsymbol}")
            elif not first_candle_exists:
                LOGGER.info(f"First candle {time_series[0]} doesnt exist for {from_date} {to_date} {interval} {instrument.tradingsymbol} returning fresh data")
                new_historical_data = self.data_broker.get_historical_data(instrument=instrument, from_date=from_date,
                                                     to_date=to_date, interval=interval.value)
                for candle in new_historical_data:
                    self._historical_data_cache_v1[instrument.tradingsymbol][interval][candle["date"]] = candle
            elif not last_candle_exists:
                # Write logic to find latest data available
                minimum_timestamp_available = None
                for candle in self._historical_data_cache_v1[instrument.tradingsymbol][interval]:
                    minimum_timestamp_available = min(from_date, candle["date"])
                new_from_date = minimum_timestamp_available
                new_historical_data = self.data_broker.get_historical_data(instrument=instrument, from_date=new_from_date,
                                                                           to_date=to_date, interval=interval.value)
                LOGGER.info(
                    f"Last candle doesnt exist for {from_date} {to_date} {interval} {instrument.tradingsymbol} returning fresh data with new from date {new_from_date}")
                for candle in new_historical_data:
                    self._historical_data_cache_v1[instrument.tradingsymbol][interval][candle["date"]] = candle
            # If data present in cache returning same data
            candles = []
            for time in time_series:
                eligible_candle = self._historical_data_cache_v1[instrument.tradingsymbol][interval].get(time)
                if eligible_candle:
                    candles.append(eligible_candle)
            LOGGER.info(f"Historical data cache looks like {self._historical_data_cache_v1}")
            LOGGER.info(f"Returning historical data {candles} for  {from_date} {to_date} {interval} {instrument.tradingsymbol}")
            return candles
        else:
            return None

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
        LOGGER.info("Initializing market data manager")
        if MarketDataManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MarketDataManager.__instance = self
        t = threading.Thread(target=self.__process_ticks_thread_funct)
        t.start()
        from Managers.BrokerManager import BrokerManager
        self.data_broker = BrokerManager.get_instance().get_data_broker()
        LOGGER.info("Done Initializing market data manager")


if __name__ == "__main__":
    MarketDataManager.get_instance()


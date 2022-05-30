import datetime as dt


class ChartBuilder:
    """
    class used for building live charts

    params:
    sym_data  -> dict containing symbol parameters
    timeframe -> candle timeframe in minutes (default = 1 min)
    """
    CANDLE = {"timestamp": None, "open": None, "high": None, "low": None, "close": None, "vol": 0}

    def __init__(self, sym_data, timeframe=1):
        self.chart = {}
        self.sym_data = sym_data
        tf = timeframe // 60
        self.timeframe = (tf * 100) + (timeframe - (tf * 60))
        self.last_tick = None
        self.running_cdl = ChartBuilder.CANDLE.copy()
        self.last_cdl = ChartBuilder.CANDLE.copy()
        self.new_candle = False
        print(
            f'chart initialised for symbol {self.sym_data["tradingsymbol"]} , timeframe {self.timeframe} min')

    def new_tick(self, ticks):
        """
        process new tick
        returns True if new candle
        """
        self.new_candle = False
        # process time
        tick_data = None
        for tick in ticks:
            if tick["instrument_token"] == self.sym_data["instrument_token"]:
                tick_data = tick
        if tick_data is None:
            print("didn't find symbol tick")
            return

        try:
            tick_time = (tick_data["exchange_timestamp"].hour * 100) + tick_data["exchange_timestamp"].minute
        except:
            tick_data["exchange_timestamp"] = tick_data["timestamp"]
            tick_time = (tick_data["exchange_timestamp"].hour * 100) + tick_data["exchange_timestamp"].minute

        try:
            x = tick_data["volume_traded"]
        except:
            tick_data["volume_traded"] = tick_data["volume"]

        if tick_time < 915:
            return

        if self.last_tick is not None:
            # print(tick_time, self.running_cdl["timestamp"])
            candle_time = (self.running_cdl["timestamp"].hour * 100) + \
                self.running_cdl["timestamp"].minute
            if (tick_time - candle_time) >= self.timeframe:
                print(self.running_cdl)
                self.chart[self.running_cdl["timestamp"]] = self.running_cdl.copy()
                self.last_cdl = self.running_cdl.copy()
                # print(self.running_cdl)
                self.new_candle = True
                self.running_cdl = ChartBuilder.CANDLE.copy()
                self.running_cdl["timestamp"] = tick_data["exchange_timestamp"]
                self.running_cdl["open"] = tick_data["last_price"]
                self.running_cdl["high"] = tick_data["last_price"]
                self.running_cdl["low"] = tick_data["last_price"]
                self.running_cdl["close"] = tick_data["last_price"]
                self.running_cdl["vol"] += tick_data["volume_traded"] - self.last_tick["volume_traded"]
            else:
                self.running_cdl["close"] = tick_data["last_price"]
                if tick_data["last_price"] > self.running_cdl["high"]:
                    self.running_cdl["high"] = tick_data["last_price"]
                if tick_data["last_price"] < self.running_cdl["low"]:
                    self.running_cdl["low"] = tick_data["last_price"]
                self.running_cdl["vol"] += tick_data["volume_traded"] - self.last_tick["volume_traded"]
        else:
            tick_time = self._sync_chart(tick_data["exchange_timestamp"])
            self.running_cdl["timestamp"] = tick_time
            self.running_cdl["open"] = tick_data["last_price"]
            self.running_cdl["high"] = tick_data["last_price"]
            self.running_cdl["low"] = tick_data["last_price"]
            self.running_cdl["close"] = tick_data["last_price"]
            print(f'first tick {tick_data["exchange_timestamp"]}')
        # process volume
        self.last_tick = tick_data
        return self.new_candle

    # chart syncing
    def _sync_chart(self, tick_timestamp):
        tick_time = (tick_timestamp.hour * 100) + tick_timestamp.minute
        time_diff = (tick_time - 915) % self.timeframe
        return tick_timestamp - dt.timedelta(minutes=time_diff)

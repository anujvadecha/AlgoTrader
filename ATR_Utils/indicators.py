import datetime
import pandas as pd


class Indicator:
    """
    base indicator class
    """

    def __init__(self, exc_trigger, timeframe=1):
        # get execution trigger
        if exc_trigger not in ("candle", "tick"):
            raise ValueError('trigger must be "candle" or " tick"')
        self.exc_trigger = exc_trigger
        # get timeframe
        if not isinstance(timeframe, int):
            raise TypeError(f'"timeframe" must be of type "int" got type "{type(timeframe)}"')
        self.timeframe = timeframe

    def _set_charting(self, chartbuilder):
        self.charting = chartbuilder

    def _set_spot_data(self, spot_data):
        self.spot_data = spot_data

    def calculate(self):
        """
        Function called for indicator calculations
        """
        pass

    def preprocessing(self, kite):
        """
        Function called for initialisation calculations
        """
        pass

    def _preprocessing(self, kite):
        """
        Function called by the indicator manager
        """
        self.preprocessing(kite)

    def _historical_data(self, kite, days_back):
        """
        NOT IMPLEMENTED
        Function used for getting the right data from Historical API
        """
        # adjust date for holidays
        # convert the timeframe


class CandleSticksChart(Indicator):
    """
    subclass that wraps the Chart Builder as an Indicator

    prams:

    """

    def __init__(self, timeframe=1, exc_trigger="tick"):
        super().__init__(exc_trigger, timeframe)
        # indicator calculated values
        self.running_cdl = None
        self.running_time = None
        self.closed_cdl = None
        self.closed_time = None
        self.chart = None
        self.new_candle = None

    def calculate(self):
        # print("calculated candlesticks")
        self.new_candle = self.charting.new_candle
        self.running_cdl = self.charting.running_cdl
        self.running_time = self.charting.running_cdl["timestamp"]
        if self.charting.new_candle:
            self.closed_cdl = self.charting.last_cdl
            self.closed_time = self.charting.last_cdl["timestamp"]

    def preprocessing(self, kite):
        self.chart = self.charting.chart


class AverageTrueRange(Indicator):
    """
    Subclass of indicator containing logic for Average True Range

    params :
    length      -> moving average length
    ma_type     -> moving average type      (NOT IMPLEMENTED)
    timeframe   -> candle timeframe
    exc_trigger -> execution trigger
    """

    def __init__(self, length=14, ma_type="rma", timeframe=1, exc_trigger="candle"):
        self.length = length
        self.ma_type = ma_type
        super().__init__(exc_trigger, timeframe)

        # indicator calculated values
        self.tr_list = []
        self.tr_rma = 0.00
        self.ATR = 0.00
        self.previous_close = 0.00

    def calculate(self):
        tr1 = self.charting.last_cdl["high"] - self.charting.last_cdl["low"]
        tr2 = abs(self.charting.last_cdl["high"] - self.previous_close)
        tr3 = abs(self.charting.last_cdl["low"] - self.previous_close)
        tr = tr1
        if self.previous_close != 0.00:
            tr = max(tr1, tr2, tr3)
        if len(self.tr_list) == self.length:
            self.tr_list = self.tr_list[1:]
        self.tr_list.append(tr)
        alpha = float(1.0 / (len(self.tr_list)))
        self.tr_rma = (alpha * tr) + (1 - alpha) * self.tr_rma
        self.ATR = round(self.tr_rma, 4)
        self.previous_close = self.charting.last_cdl["close"]

    def preprocessing(self, kite):
        to_date = datetime.datetime.now() - datetime.timedelta(days=1)  # NEED TO ADD ADJUSTMENT FOR HOLIDAYS
        from_date = to_date - datetime.timedelta(days=7)
        hist_candles = f'{self.timeframe}minute'
        if self.timeframe == 1:
            hist_candles = "minute"
        hist = kite.historical_data(self.spot_data["instrument_token"], from_date.strftime(
            "%Y-%m-%d"), to_date.strftime("%Y-%m-%d"), hist_candles)
        hist_df = pd.DataFrame(hist)
        print(hist_df.head())
        print(hist_df.tail())
        for index, row in hist_df.iterrows():
            tr1 = row["high"] - row["low"]
            tr2 = abs(row["high"] - self.previous_close)
            tr3 = abs(row["low"] - self.previous_close)
            tr = tr1
            if self.previous_close != 0.00:
                tr = max(tr1, tr2, tr3)
            if len(self.tr_list) == self.length:
                self.tr_list = self.tr_list[1:]
            self.tr_list.append(tr)
            alpha = float(1.0 / (len(self.tr_list)))
            self.tr_rma = (alpha * tr) + (1 - alpha) * self.tr_rma
            self.ATR = round(self.tr_rma, 4)
            self.previous_close = row["close"]
        print(self.ATR)


class ParabolicSAR(Indicator):
    """
    Subclass of indicator containing logic for Parabolic SAR

    params:
    start          -> increment starting value
    increment_step -> increment step
    inc_max        -> maximum increment value
    timeframe      -> candle timeframe
    exc_trigger    -> execution trigger
    """

    def __init__(self, start=0.02, increment_step=0.02, inc_max=0.2, timeframe=1, exc_trigger="candle"):
        # params
        self.start = start
        self.increment_step = increment_step
        self.inc_max = inc_max
        super().__init__(exc_trigger, timeframe)

        # indicator calculated values
        self.ep = None
        self.trend = 0
        self.af = 0.00
        self.PSAR = float('nan')
        self.prev_candle = None
        self.prev_PSAR = 0.00

    def calculate(self):
        candle = self.charting.last_cdl.copy()
        # starting the psar
        if self.trend == 0:
            self.trend = 1
            self.PSAR = candle["low"]
            self.af = self.start
            self.ep = candle["high"]
        else:
            if self.trend > 0:
                # bullish trend calculations
                self.PSAR = self.PSAR + (self.af * (self.ep - self.PSAR))
                # check for reversal
                if candle["low"] <= self.prev_PSAR:
                    self.trend = -1
                    self.PSAR = self.ep
                    self.af = self.start
                    self.ep = candle["low"]
                else:
                    if candle["high"] > self.ep:
                        self.ep = candle["high"]
                        self.af = min(self.af + self.increment_step, self.inc_max)
                        self.PSAR = self.prev_PSAR + (self.af * (self.ep - self.prev_PSAR))
                    if candle["low"] < self.PSAR:
                        self.PSAR = candle["low"]
            else:
                # bearish trend calculations
                self.PSAR = self.PSAR - (self.af * (self.PSAR - self.ep))
                # check for reversal
                if candle["high"] >= self.prev_PSAR:
                    self.trend = 1
                    self.PSAR = self.ep
                    self.af = self.start
                    self.ep = candle["high"]
                else:
                    if candle["low"] < self.ep:
                        self.ep = candle["low"]
                        self.af = min(self.af + self.increment_step, self.inc_max)
                        self.PSAR = self.prev_PSAR - (self.af * (self.prev_PSAR - self.ep))
                    if candle["high"] > self.PSAR:
                        self.PSAR = candle["high"]
        self.prev_candle = candle.copy()
        self.PSAR = round(self.PSAR, 4)
        self.prev_PSAR = self.PSAR

    def preprocessing(self, kite):
        to_date = datetime.datetime.now() - datetime.timedelta(days=1)  # NEED TO ADD ADJUSTMENT FOR HOLIDAYS
        from_date = to_date - datetime.timedelta(days=7)
        hist_candles = f'{self.timeframe}minute'
        if self.timeframe == 1:
            hist_candles = "minute"
        hist = kite.historical_data(self.spot_data["instrument_token"], from_date.strftime(
            "%Y-%m-%d"), to_date.strftime("%Y-%m-%d"), hist_candles)
        hist_df = pd.DataFrame(hist)
        print(hist_df.head())
        print(hist_df.tail())
        for index, row in hist_df.iterrows():
            candle = row
            if self.trend == 0:
                self.trend = 1
                self.PSAR = candle["low"]
                self.af = self.start
                self.ep = candle["high"]
            else:
                if self.trend > 0:
                    # bullish trend calculations
                    self.PSAR = self.PSAR + (self.af * (self.ep - self.PSAR))
                    # check for reversal
                    if candle["low"] <= self.prev_PSAR:
                        self.trend = -1
                        self.PSAR = self.ep
                        self.af = self.start
                        self.ep = candle["low"]
                    else:
                        if candle["high"] > self.ep:
                            self.ep = candle["high"]
                            self.af = min(self.af + self.increment_step, self.inc_max)
                            self.PSAR = self.prev_PSAR + (self.af * (self.ep - self.prev_PSAR))
                        if candle["low"] < self.PSAR:
                            self.PSAR = candle["low"]
                else:
                    # bearish trend calculations
                    self.PSAR = self.PSAR - (self.af * (self.PSAR - self.ep))
                    # check for reversal
                    if candle["high"] >= self.prev_PSAR:
                        self.trend = 1
                        self.PSAR = self.ep
                        self.af = self.start
                        self.ep = candle["high"]
                    else:
                        if candle["low"] < self.ep:
                            self.ep = candle["low"]
                            self.af = min(self.af + self.increment_step, self.inc_max)
                            self.PSAR = self.prev_PSAR - (self.af * (self.prev_PSAR - self.ep))
                        if candle["high"] > self.PSAR:
                            self.PSAR = candle["high"]
            self.prev_candle = candle.copy()
            self.PSAR = round(self.PSAR, 4)
            self.prev_PSAR = self.PSAR


class Supertrend(Indicator):
    """
    Subclass of indicator containing logic for Supertrend

    params:
    atr_length   -> atr length
    factor       -> atr multiple factor
    timeframe    -> candle timeframe
    exc_trigger  -> execution trigger
    """

    def __init__(self, atr_length=10, factor=3, timeframe=1, exc_trigger="candle"):
        self.atr_length = atr_length
        self.factor = factor
        super().__init__(exc_trigger, timeframe)

        # indicator calculated values
        self.tr_list = []
        self.tr_rma = 0.00
        self.atr = 0.00
        self.previous_close = 0.00
        self.upper_band = 0
        self.lower_band = 0
        self.supertrend = 0
        self.trend = 0

    def calculate(self):
        candle = self.charting.last_cdl.copy()

        tr1 = candle["high"] - candle["low"]
        tr2 = abs(candle["high"] - self.previous_close)
        tr3 = abs(candle["low"] - self.previous_close)
        tr = tr1
        if self.previous_close != 0.00:
            tr = max(tr1, tr2, tr3)
        if len(self.tr_list) == self.atr_length:
            self.tr_list = self.tr_list[1:]
        self.tr_list.append(tr)
        self.atr = round(sum(self.tr_list) / len(self.tr_list), 3)

        hla = (candle["high"] + candle["low"]) / 2.0
        upper_basic = hla + (self.factor * self.atr)
        lower_basic = hla - (self.factor * self.atr)

        upper_band_final = self.upper_band
        lower_band_final = self.lower_band

        if upper_basic < self.upper_band or self.previous_close > self.upper_band:
            upper_band_final = upper_basic

        if lower_basic > self.lower_band or self.previous_close < self.lower_band:
            lower_band_final = lower_basic

        if self.supertrend == self.upper_band:
            if candle["close"] > upper_band_final:
                self.supertrend = lower_band_final
                self.trend = 1
            elif candle["close"] < upper_band_final:
                self.supertrend = upper_band_final
        elif self.supertrend == self.lower_band:
            if candle["close"] > lower_band_final:
                self.supertrend = lower_band_final
            elif candle["close"] < lower_band_final:
                self.supertrend = upper_band_final
                self.trend = -1

        self.upper_band = upper_band_final
        self.lower_band = lower_band_final
        self.previous_close = candle["close"]

    def preprocessing(self, kite):
        to_date = datetime.datetime.now() - datetime.timedelta(days=1)  # NEED TO ADD ADJUSTMENT FOR HOLIDAYS
        from_date = to_date - datetime.timedelta(days=7)
        hist_candles = f'{self.timeframe}minute'
        if self.timeframe == 1:
            hist_candles = "minute"
        hist = kite.historical_data(self.spot_data["instrument_token"], from_date.strftime(
            "%Y-%m-%d"), to_date.strftime("%Y-%m-%d"), hist_candles)
        hist_df = pd.DataFrame(hist)
        print(hist_df.head())
        print(hist_df.tail())
        for index, row in hist_df.iterrows():
            candle = row
            tr1 = candle["high"] - candle["low"]
            tr2 = abs(candle["high"] - self.previous_close)
            tr3 = abs(candle["low"] - self.previous_close)
            tr = tr1
            if self.previous_close != 0.00:
                tr = max(tr1, tr2, tr3)
            if len(self.tr_list) == self.atr_length:
                self.tr_list = self.tr_list[1:]
            self.tr_list.append(tr)
            self.atr = round(sum(self.tr_list) / len(self.tr_list), 3)

            hla = (candle["high"] + candle["low"]) / 2.0
            upper_basic = hla + (self.factor * self.atr)
            lower_basic = hla - (self.factor * self.atr)

            upper_band_final = self.upper_band
            lower_band_final = self.lower_band

            if upper_basic < self.upper_band or self.previous_close > self.upper_band:
                upper_band_final = upper_basic

            if lower_basic > self.lower_band or self.previous_close < self.lower_band:
                lower_band_final = lower_basic

            if self.supertrend == self.upper_band:
                if candle["close"] > upper_band_final:
                    self.supertrend = lower_band_final
                    self.trend = 1
                elif candle["close"] < upper_band_final:
                    self.supertrend = upper_band_final
            elif self.supertrend == self.lower_band:
                if candle["close"] > lower_band_final:
                    self.supertrend = lower_band_final
                elif candle["close"] < lower_band_final:
                    self.supertrend = upper_band_final
                    self.trend = -1

            self.upper_band = upper_band_final
            self.lower_band = lower_band_final
            self.previous_close = candle["close"]


class Stochastic(Indicator):
    """
    Subclass of indicator containing logic for Stochastic

    params:
    k_length     -> %k length
    k_smooth     -> %k smoothing factor
    d_smooth     -> %d smoothing factor
    timeframe    -> candle timeframe
    exc_trigger  -> execution trigger
    """

    def __init__(self, k_length=14, k_smooth=1, d_smooth=3, timeframe=1, exc_trigger="candle"):
        self.k_length = k_length
        self.k_smooth = k_smooth
        self.d_smooth = d_smooth
        super().__init__(exc_trigger, timeframe)

        # indicator calculated values
        self.high_list = []
        self.low_list = []
        self.k_list = []
        self.k_value = float('nan')
        self.d_list = []
        self.d_value = float('nan')
        self.signal = None

    def calculate(self):
        closed = self.charting.last_cdl.copy()

        if len(self.high_list) > self.k_length:
            self.high_list = self.high_list[1:]
        self.high_list.append(closed["high"])
        highest = max(self.high_list)

        if len(self.low_list) > self.k_length:
            self.low_list = self.low_list[1:]
        self.low_list.append(closed["low"])
        lowest = min(self.low_list)

        if highest - lowest <= 0:
            return

        k = (closed["close"] - lowest) / (highest - lowest) * 100
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

    def preprocessing(self, kite):
        to_date = datetime.datetime.now() - datetime.timedelta(days=1)  # NEED TO ADD ADJUSTMENT FOR HOLIDAYS
        from_date = to_date - datetime.timedelta(days=7)
        hist_candles = f'{self.timeframe}minute'
        if self.timeframe == 1:
            hist_candles = "minute"
        hist = kite.historical_data(self.spot_data["instrument_token"], from_date.strftime(
            "%Y-%m-%d"), to_date.strftime("%Y-%m-%d"), hist_candles)
        hist_df = pd.DataFrame(hist)
        print(hist_df.head())
        print(hist_df.tail())
        for index, row in hist_df.iterrows():
            closed = row

            if len(self.high_list) > self.k_length:
                self.high_list = self.high_list[1:]
            self.high_list.append(closed["high"])
            highest = max(self.high_list)

            if len(self.low_list) > self.k_length:
                self.low_list = self.low_list[1:]
            self.low_list.append(closed["low"])
            lowest = min(self.low_list)

            if highest - lowest <= 0:
                return

            k = (closed["close"] - lowest) / (highest - lowest) * 100
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


def pivotpoints_calculation(data):
    day_open = data["open"]
    day_high = data["high"]
    day_low = data["low"]
    day_close = data["close"]
    pp = (day_high + day_low + day_close) / 3.0
    lb = (day_high + day_low) / 2.0
    ub = (pp - lb) + pp
    r1 = (2 * pp) - day_low
    r2 = pp + (day_high - day_low)
    r3 = r1 + (day_high - day_low)
    s1 = (2 * pp) - day_high
    s2 = pp - (day_high - day_low)
    s3 = s1 - (day_high - day_low)
    tc = max(lb, ub)
    bc = min(lb, ub)
    out = {'pivot_point': round(pp, 2),
           'upper_band': round(tc, 2),
           'lower_band': round(bc, 2),
           'r1': round(r1, 2),
           'r2': round(r2, 2),
           'r3': round(r3, 2),
           's1': round(s1, 2),
           's2': round(s2, 2),
           's3': round(s3, 2),
           'pdl': data["low"],
           'pdh': data["high"]}
    return out


class PivotPoints(Indicator):
    """
    """

    def __init__(self,timeframe):
        exc_trigger = "candle"
        super().__init__(exc_trigger, timeframe)
        self.pivots = {'pivot_point': None,
                       'upper_band': None,
                       'lower_band': None,
                       'r1': None,
                       'r2': None,
                       'r3': None,
                       's1': None,
                       's2': None,
                       's3': None}

    def calculate(self):
        return

    def preprocessing(self, kite):
        to_date = datetime.datetime.now() - datetime.timedelta(days=1)  # NEED TO ADD ADJUSTMENT FOR HOLIDAYS
        from_date = to_date - datetime.timedelta(days=7)
        hist_candles = 'day'
        hist = kite.historical_data(self.spot_data["instrument_token"], from_date.strftime(
            "%Y-%m-%d"), to_date.strftime("%Y-%m-%d"), hist_candles)
        hist_df = pd.DataFrame(hist)
        yest_data = hist_df.iloc[-1]
        self.pivots = pivotpoints_calculation(yest_data)

    def check_pivot(self, candle, pivot_points):
        pivot_range = ""
        pivot = self.pivots

        # find lower bound
        lower_bound = ""
        if candle["close"] > pivot["r3"]:
            lower_bound = "r3"
        elif candle["close"] > pivot["r2"]:
            lower_bound = "r2"
        elif candle["close"] > pivot["r1"]:
            lower_bound = "r1"
        elif candle["close"] > pivot["upper_band"]:
            lower_bound = "upper_band"
        elif candle["close"] > pivot["pivot_point"]:
            lower_bound = "pivot_point"
        elif candle["close"] > pivot["lower_band"]:
            lower_bound = "lower_band"
        elif candle["close"] > pivot["s1"]:
            lower_bound = "s1"
        elif candle["close"] > pivot["s2"]:
            lower_bound = "s2"
        elif candle["close"] > pivot["s3"]:
            lower_bound = "s3"
        elif candle["close"] < pivot["s3"]:
            lower_bound = "na"

        # find upper bound
        upper_bound = ""
        if candle["close"] < pivot["s3"]:
            upper_bound = "s3"
        elif candle["close"] < pivot["s2"]:
            upper_bound = "s2"
        elif candle["close"] < pivot["s1"]:
            upper_bound = "s1"
        elif candle["close"] < pivot["lower_band"]:
            upper_bound = "lower_band"
        elif candle["close"] < pivot["pivot_point"]:
            upper_bound = "pivot_point"
        elif candle["close"] < pivot["upper_band"]:
            upper_bound = "upper_band"
        elif candle["close"] < pivot["r1"]:
            upper_bound = "r1"
        elif candle["close"] < pivot["r2"]:
            upper_bound = "r2"
        elif candle["close"] < pivot["r3"]:
            upper_bound = "r3"
        elif candle["close"] > pivot["r3"]:
            upper_bound = "na"

        # correct for pdh and pdl
        if upper_bound != "na":
            if pivot[upper_bound] > pivot["pdl"] > candle["close"]:
                upper_bound = "pdl"
            elif pivot[upper_bound] > pivot["pdh"] > candle["close"]:
                upper_bound = "pdh"

        if lower_bound != "na":
            if pivot[lower_bound] < pivot["pdh"] < candle["close"]:
                lower_bound = "pdh"
            elif pivot[lower_bound] < pivot["pdl"] < candle["close"]:
                lower_bound = "pdl"

        # final bands
        final_band = ""

        if upper_bound == "na":
            final_band = "> r3"
            pivot_range = final_band
            return pivot_range

        if lower_bound == "na":
            final_band = "< s3"
            pivot_range = final_band
            return pivot_range

        if upper_bound == "lower_band":
            upper_bound = "bc"

        if upper_bound == "pivot_point":
            upper_bound = "pp"

        if upper_bound == "upper_band":
            upper_bound = "tc"

        if lower_bound == "lower_band":
            lower_bound = "bc"

        if lower_bound == "pivot_point":
            lower_bound = "pp"

        if lower_bound == "upper_band":
            lower_bound = "tc"

        final_band = upper_bound + "-" + lower_bound
        pivot_range = final_band

        return pivot_range

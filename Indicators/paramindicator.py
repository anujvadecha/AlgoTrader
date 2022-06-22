from Core.Enums import CandleInterval
from Indicators.indicator_base import Indicator
from Indicators.psar import ParabolicSAR
from Indicators.stoch import Stochastic
from Indicators.supertrend import SuperTrend


class ParamIndicator(Indicator):

    def __init__(self, timeframe = CandleInterval.fifteen_min, instrument=None):
        self.instrument = instrument
        self.supertrend = SuperTrend(instrument=instrument,
                                     timeframe=CandleInterval.fifteen_min,
                                     atr_length=10,
                                     factor=3)

        self.parabolic_sar = ParabolicSAR(instrument=instrument,
                                          timeframe=CandleInterval.fifteen_min,
                                          start=0.02,
                                          increment_step=0.02,
                                          inc_max=0.2)
        super().__init__(timeframe, instrument)

    def calculate(self, candle=None):
        self.supertrend.calculate(candle)
        self.parabolic_sar.calculate(candle)
        psar = self.parabolic_sar.trend
        st = self.supertrend.trend
        param = ""
        # parameter determinations
        if psar > 0 and st > 0:
            param = "param1"
        elif psar < 0 and st > 0:
            param = "param2"
        elif psar > 0 and st < 0:
            param = "param3"
        elif psar < 0 and st < 0:
            param = "param4"
        return param

from ATR_Utils.chart_manager import ChartManager


class IndicatorManager:
    """
    Manager class for indicators
    responsible for indicator calculations
    """

    def __init__(self, spot_data, kite):
        self.indicator_count = 0
        self.indicators = []
        self.spot_data = spot_data
        self.candle_triggered = []
        self.tick_triggered = []
        self.cm = ChartManager(self.spot_data)
        self.kite = kite

    def add_indicators(self, indicators):
        if not isinstance(indicators, list):
            raise TypeError(f'"indicators" must be of type "list" got type "{type(indicators)}" ')
        for indicator in indicators:
            # extract timeframe
            tf = indicator.timeframe
            charting = self.cm.new_chart(tf)
            # link chart
            indicator._set_charting(charting)
            indicator._set_spot_data(self.spot_data)
            if indicator.exc_trigger == "candle":
                self.candle_triggered.append(indicator)
            else:
                self.tick_triggered.append(indicator)
            indicator._preprocessing(self.kite)

    def new_ticks(self, ticks):
        cdls_sig = self.cm.new_tick(ticks)
        for indicator in self.candle_triggered:
            if cdls_sig[indicator.timeframe]:
                indicator.calculate()
        for indicator in self.tick_triggered:
            indicator.calculate()

    def add_logic(self, logic):
        # extract timeframe
        tf = logic.indicator.timeframe
        charting = self.cm.new_chart(tf)
        # link chart
        logic.indicator._set_charting(charting)
        logic.indicator._set_spot_data(self.spot_data)
        if logic.indicator.exc_trigger == "candle":
            self.candle_triggered.append(logic.indicator)
        else:
            self.tick_triggered.append(logic.indicator)
        logic.indicator._preprocessing(self.kite)

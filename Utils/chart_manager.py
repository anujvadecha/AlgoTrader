from Utils.chart_builder import ChartBuilder


class ChartManager:
    """
    Manager class for charts
    """

    def __init__(self, sym_data):
        self.sym_data = sym_data
        self.chart_builders = {}

    def new_chart(self, timeframe=1):
        if timeframe not in self.chart_builders.keys():
            new_chart = ChartBuilder(self.sym_data, timeframe)
            self.chart_builders[timeframe] = new_chart
        return self.chart_builders[timeframe]

    def new_tick(self, ticks):
        new_candles_flags = {}
        for timeframe in self.chart_builders:
            new_candles_flags[timeframe] = self.chart_builders[timeframe].new_tick(ticks)
        return new_candles_flags

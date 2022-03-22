from datetime import timedelta

from Managers.MarketDataManager import MarketDataManager


class PivotIndicator:

    def _calculate_pivot_points(self, candle):
        day_open = candle["open"]
        day_high = candle["high"]
        day_low = candle["low"]
        day_close = candle["close"]
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
        return {"pdl": day_low, "pdh": day_high, "bc": bc, "tc": tc, "pp": pp, "r1": r1, "r2": r2, "r3": r3, "s1": s1, "s2": s2, "s3": s3, "lb": lb, "ub": ub}

    def calculate(self, instrument ,from_date, to_date, interval=None):
        historical_data = MarketDataManager.get_instance().get_historical_data(instrument=instrument, from_date=from_date, to_date=to_date, interval=interval)
        pivot_data = {}
        for data in historical_data:
            day_of_calculation = data['date']+timedelta(days=1)
            pivot_data[day_of_calculation] =  self._calculate_pivot_points(data)
        return pivot_data

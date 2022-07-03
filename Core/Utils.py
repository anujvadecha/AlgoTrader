from datetime import datetime, timedelta
from decimal import Decimal

from pytimeparse.timeparse import timeparse

from Core.Enums import CandleInterval
import logging

LOGGER = logging.getLogger(__name__)

def ceil_dt(dt, delta):
    return dt + (datetime.min - dt) % delta


def is_within_market_time_range(timestamp):
    start_time_eod = datetime.combine(timestamp.date(),
                                      datetime.strptime("09:15:00.00", '%H:%M:%S.%f').time())
    end_time_eod = datetime.combine(timestamp.date(), datetime.strptime("15:30:00.00", '%H:%M:%S.%f').time())
    if start_time_eod <= timestamp <= end_time_eod:
        return True
    return False



def get_candle_time_series_for_date_range(from_date, to_date, interval: CandleInterval):
    import pandas as pd
    frequency_seconds = timeparse(interval.value) if interval != CandleInterval.day else 86400

    from_date = ceil_dt(from_date, timedelta(seconds=frequency_seconds)) if interval !=CandleInterval.hourly else ceil_dt(from_date, timedelta(seconds=timeparse(CandleInterval.fifteen_min.value))).replace(minute=15)
    LOGGER.info(f"date range requested from {from_date} to {to_date}")
    range = pd.date_range(start=from_date, end=to_date, freq=f"{frequency_seconds}S").to_pydatetime()
    if interval == CandleInterval.day:
        return list(range)
    else:
        range = list(time for time in range if is_within_market_time_range(time) and time < (datetime.now() - timedelta(seconds=frequency_seconds)))
    LOGGER.info(f"Range created is {range} {range[0] if len(range) else None} {range[-1] if len(range) else None}")
    return range

def to_decimal(val, exp=Decimal('0.01')):
    """
    Convert value to the Decimal type, rounding to fixed exponent: restricting
     decimal places to `precision` (default=TWO_PLACES).
    To override, pass precision: .e.g precision=FOUR_PLACES for
     4 decimal places of precision.

    Args:
        val (str, int, decimal.Decimal): Value to convert to decimal
        exp (decimal.Decimal): To set number of decimal places.

    Returns: decimal.Decimal
    """
    return Decimal(val).quantize(exp)

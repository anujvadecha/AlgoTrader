import traceback
from datetime import datetime, timedelta
import schedule
import pandas as pd
from Core.Enums import CandleInterval, StrategyState
from Indicators.PivotIndicator import PivotIndicator
from Core.Strategy import Strategy
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Models.Models import Instrument
import logging

LOGGER = logging.getLogger(__name__)


class OptionMarketDataCollector(Strategy):
    strategy_name = "Choppy"
    trade_limit = 1
    number_of_trades = 0

    def _initiate_inputs(self, inputs):
        self.instrument = Instrument(symbol=inputs["instrument"])
        self.order_instrument = Instrument(symbol=inputs["order_instrument"])
        self.option_side = inputs["option_side"]
        self.option_quantity = inputs["option_quantity"]
        self.order_quantity = int(inputs["order_quantity"])
        self.option_expiry = inputs["option_expiry"]

    def on_create(self, inputs):
        self._initiate_inputs(inputs)
        from_date = datetime.now() - timedelta(days=5)
        to_date = datetime.now()
        yesterdays_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                               from_date=from_date, to_date=to_date,
                                                                               interval=CandleInterval.fifteen_min)

    def define_inputs(self):
        order_instruments = InstrumentManager.get_instance().get_futures_for_instrument(symbol="NIFTY")
        order_instruments.extend(InstrumentManager.get_instance().get_futures_for_instrument(symbol="BANKNIFTY"))
        option_intruments = InstrumentManager.get_instance().get_call_options_for_instrument(
            "BANKNIFTY" )
        expiries = sorted(set(str(instrument.expiry) for instrument in option_intruments))
        instruments = ["NIFTY 50",  "NIFTY BANK" ]
        return {
            "instrument": instruments,
            "option_expiry": list(expiries),
        }


    def calculate_triggers(self):
        try:
            pass
        except Exception as e:
            LOGGER.info(traceback.format_exc())
            self.add_info_user_message(f"Failure occured while calculating triggers {e} stopping strategy")
            self.stop()
            LOGGER.exception(f"Exception occured for calculate_triggers for {self.inputs}", e)
            raise e

    def schedule_tasks(self):
        schedule.every(1).seconds.do(self.calculate_triggers)

    def stop(self):
        if self.entry and self.entry_side == "BUY":
            self.place_exit_order("SELL", "STOP_SQUARE_OFF")
        if self.entry and self.entry_side == "SELL":
            self.place_exit_order("BUY", "STOP_SQUARE_OFF")
        super().stop()

from datetime import datetime, timedelta
import enum
import pytz
import schedule
import pandas as pd
from dateutil.tz import tzoffset

from Core.Enums import CandleInterval
from Indicators.PivotIndicator import PivotIndicator
from Core.Strategy import Strategy
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Models.Models import Instrument
import logging

LOGGER = logging.getLogger(__name__)


class Choppy(Strategy):
    strategy_name = "Choppy"
    trade_limit = 1
    number_of_trades = 0

    def _check_pivot(self, candle, pivot):
        print(f"Candle is {candle} pivot {pivot}")
        pivot["upper_band"] = pivot["tc"]
        pivot["lower_band"] = pivot["bc"]
        pivot["pivot_point"] = pivot["pp"]
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

    def place_entry_order(self, side, identifier=None):
        self.option_entry_instrument = None
        self.add_info_user_message(
            f"Placing entry order for {self.order_instrument} {side} {self.order_quantity} {identifier}")
        # Futures order
        if self.order_type != "OPTIONS_ONLY":
            self.broker.place_market_order(instrument=self.order_instrument, side=side,
                                       quantity=self.order_quantity, type="CNC")
        # Options order
        if self.order_type != "FUTURES_ONLY":
            if self.entry_price % 100 < 50:
                targeted_strike_price = self.entry_price - self.entry_price%100
            else:
                targeted_strike_price = self.entry_price + (100 - self.entry_price % 100)
            if side=="BUY":
                option_intruments = InstrumentManager.get_instance().get_call_options_for_instrument("BANKNIFTY" if self.instrument.tradingsymbol=="NIFTY BANK" else "NIFTY", strike=targeted_strike_price)
            else:
                option_intruments = InstrumentManager.get_instance().get_put_options_for_instrument(
                    "BANKNIFTY" if self.instrument.tradingsymbol == "NIFTY BANK" else "NIFTY",
                    strike=targeted_strike_price)
            for optioninstr in option_intruments:
                if str(optioninstr.expiry) == self.option_expiry:
                    self.option_entry_instrument = optioninstr
                    break
            if self.option_entry_instrument:
                self.add_info_user_message(
                    f"Placing entry order for {self.option_entry_instrument} BUY {self.option_quantity} {identifier}")

                self.broker.place_market_order(instrument=self.option_entry_instrument, side="BUY",
                                               quantity=self.option_quantity, type="CNC")
            else:
                self.add_info_user_message(f"Option entry not found for {targeted_strike_price} {self.instrument.tradingsymbol}")
        self.entry = True
        self.number_of_trades = self.number_of_trades + 1

    def place_exit_order(self, side, identifier=None):
        self.add_info_user_message(
            f"Placing exit order for {self.order_instrument} {side} {self.order_quantity} {identifier}")
        self.broker.place_market_order(instrument=self.order_instrument,
                                       side=side, quantity=self.order_quantity,
                                       type="CNC")
        if self.option_entry_instrument:
            self.add_info_user_message(
                f"Placing exit order for {self.option_entry_instrument} SELL {self.option_quantity} {identifier}")
            self.broker.place_market_order(instrument=self.option_entry_instrument,
                                           side="SELL", quantity=self.option_quantity,
                                           type="CNC")
        self.entry = False

    def _initiate_inputs(self, inputs):
        self.instrument = Instrument(symbol=inputs["instrument"])
        self.order_instrument = Instrument(symbol=inputs["order_instrument"])
        self.option_side = inputs["option_side"]
        self.option_quantity = inputs["option_quantity"]
        self.order_quantity = int(inputs["order_quantity"])
        self.option_expiry = inputs["option_expiry"]

    def on_create(self, inputs):
        logging.info("Adding test log")
        input_file = inputs['input_file']
        input_df = None
        if input_file.endswith('.csv'):
            input_df = pd.read_csv(input_file)
        elif input_file.endswith('.xlsx'):
            input_df = pd.read_excel(input_file)
        conditions = input_df.to_dict('records')
        from_date = datetime.now() - timedelta(days=7)
        to_date = datetime.now() - timedelta(hours=6)
        interval = CandleInterval.day
        self._initiate_inputs(inputs)
        indicator_values = PivotIndicator().calculate(instrument=self.instrument, from_date=from_date, to_date=to_date,
                                                      interval=interval)
        self.order_type = inputs["orders_type"]
        self.yesterdays_pivot_points = indicator_values[-2]
        self.yesterdays_date = indicator_values[-1]["date"]
        self.add_info_user_message(f"Yesterdays pivot points {self.yesterdays_pivot_points}")
        self.pivot_points = indicator_values[-1]
        from_date = datetime.now() - timedelta(days=5)
        to_date = datetime.now()
        yesterdays_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                               from_date=from_date, to_date=to_date,
                                                                               interval=CandleInterval.fifteen_min)
        last_candle = None
        for data in yesterdays_data:
            if data['date'].date() == self.yesterdays_date.date():
                last_candle = data
        print(f"yesterdays close {last_candle}")
        self.yesterdays_candle = last_candle
        self.yesterdays_choppy_range = self._check_pivot(self.yesterdays_candle, pivot=self.yesterdays_pivot_points)

        valid_conditions = []
        for condition in conditions:
            if condition['yesterdays_candle'] == self.yesterdays_choppy_range and condition['script'] == inputs[
                "instrument"]:
                valid_conditions.append(condition)
        self.valid_conditions = valid_conditions
        self.add_info_user_message(f"Pivot points {self.pivot_points}")
        self.add_info_user_message(f"Yesterdays choppy range is {self.yesterdays_choppy_range}")
        self.entry = False
        self.subscribe(self.instrument, self.on_ticks)

    def define_inputs(self):
        order_instruments = InstrumentManager.get_instance().get_futures_for_instrument(symbol="NIFTY")
        order_instruments.extend(InstrumentManager.get_instance().get_futures_for_instrument(symbol="BANKNIFTY"))
        order_instrument_names = [instrument.tradingsymbol for instrument in order_instruments]
        option_intruments = InstrumentManager.get_instance().get_call_options_for_instrument(
            "BANKNIFTY" )
        expiries = sorted(set(str(instrument.expiry) for instrument in option_intruments))
        instruments = ["NIFTY 50",  "NIFTY BANK" ]
        return {
            "input_file": "resources/Choppy_conditions.csv",
            "instrument": instruments,
            "orders_type": [ "FUTURE_AND_OPTIONS","FUTURES_ONLY", "OPTIONS_ONLY"],
            "order_instrument": order_instrument_names,
            "order_quantity": "50",
            "option_quantity": "50",
            "option_side": ["BUY"],
            "option_expiry": list(expiries)
        }

    def on_ticks(self, tick):
        if tick.symbol == self.instrument.tradingsymbol and self.entry:
            if self.entry_side == "BUY":
                if tick.ltp >= self.target_price:
                    self.place_exit_order("SELL", "TARGET_ACHIEVED")
            if self.entry_side == "SELL":
                if tick.ltp <= self.target_price:
                    self.place_exit_order("BUY", "TARGET_ACHIEVED")

    def calculate_triggers(self):
        try:
            now = datetime.now()
            if now.hour == 3 and now.minute==15 and self.entry:
                self.place_exit_order("BUY" if self.entry_side=="SELL" else "SELL", "AUTOMATIC_SQUARE_OFF")
            # if now.minute % 15 == 0:
            if now.minute % 1 == 0:
                #     TODO to uncomment
                if not self.entry and self.number_of_trades < self.trade_limit:
                        # and now.hour == 9 and now.minute == 30:
                    LOGGER.info(f"{datetime.now()} calculate triggers called")
                    from_date = datetime.now() - timedelta(hours=6)
                    to_date = datetime.now()
                    recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                                       from_date=from_date,
                                                                                       to_date=to_date,
                                                                                       interval=CandleInterval.fifteen_min)
                    for data in recent_data:
                        if data['date'].hour == 9 and data['date'].minute == 15:
                            bullish_bearish = 'bullish' if data['close'] > data['open'] else 'bearish'
                            candle_range = self._check_pivot(data, pivot=self.pivot_points)
                            self.add_info_user_message(
                                f"9:15 candle identified {bullish_bearish} with candle range {candle_range}")
                            for condition in self.valid_conditions:
                                if condition['todays_candle'] == candle_range \
                                        and condition['candle_type'] == bullish_bearish:
                                    if condition['decision'] != 'no_trade':
                                        self.entry_price = data['close']
                                        self.entry_side = condition['decision'].upper()
                                        if self.entry_price > self.pivot_points["tc"] and self.entry_side == "SELL":
                                            self.target_points = 120 if self.instrument.tradingsymbol=="NIFTY BANK" else 40
                                        if self.entry_price > self.pivot_points["tc"] and self.entry_side == "BUY":
                                            self.target_points = 180 if self.instrument.tradingsymbol=="NIFTY BANK" else 60
                                        if self.entry_price < self.pivot_points["bc"] and self.entry_side == "SELL":
                                            self.target_points = 180 if self.instrument.tradingsymbol=="NIFTY BANK" else 60
                                        if self.entry_price < self.pivot_points["bc"] and self.entry_side == "BUY":
                                            self.target_points = 120 if self.instrument.tradingsymbol=="NIFTY BANK" else 40
                                        self.add_info_user_message(
                                            f"Condition {condition} satisfied, triggering order")
                                        self.entry = True
                                        self.place_entry_order(side=condition['decision'].upper())
                                        self.target_price = self.entry_price + self.target_points if self.entry_side == "BUY" else self.entry_price - self.target_points
                                        ranges = candle_range.split("-")
                                        upper_range = max(
                                            self.pivot_points[range_identifer] for range_identifer in ranges)
                                        lower_range = min(
                                            self.pivot_points[range_identifer] for range_identifer in ranges)
                                        self.sl = upper_range if self.entry_side == "SELL" else lower_range
                                        self.add_info_user_message(
                                            f"Target points{self.target_points} target {self.target_price} side {self.entry_side} SL {self.sl}")

                if self.entry:
                    # Calculating SL exit on 15 minute
                    from_date = datetime.now() - timedelta(minutes=30)
                    to_date = datetime.now()
                    recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                                       from_date=from_date,
                                                                                       to_date=to_date,
                                                                                       interval=CandleInterval.fifteen_min)
                    last_candle = recent_data[-1]
                    if self.entry_side == "BUY":
                        if last_candle["close"] <= self.sl:
                            self.place_exit_order("SELL", "SL_TRIGGERED")
                    if self.entry_side == "SELL":
                        if last_candle["close"] >= self.sl:
                            self.place_exit_order("BUY", "SL_TRIGGERED")
        except Exception as e:
            self.add_info_user_message(f"Failure occured while calculating triggers {e} stopping strategy")
            self.stop()
            raise e

    def schedule_tasks(self):
        schedule.every(1).seconds.do(self.calculate_triggers)

    def stop(self):
        super().stop()

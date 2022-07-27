import json
import traceback
from datetime import datetime, timedelta
import schedule
import pandas as pd
from Core.Enums import CandleInterval, StrategyState, TradeIdentifier
from Indicators.PivotIndicator import PivotIndicator
from Core.Strategy import Strategy
from Indicators.paramindicator import ParamIndicator
from Indicators.vwap import VolumeWeightedAveragePrice
from Indicators.stoch import Stochastic
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Models.Models import Instrument
import logging

LOGGER = logging.getLogger(__name__)


class Eighteen(Strategy):
    strategy_name = "Eighteen"
    trade_limit = 1
    number_of_trades = 0
    open_positions = []
    last_calculated_entry = None

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

    def place_entry_order(self, side, entry_candle, identifier=TradeIdentifier.ENTRY, reversal=False):
        self.entry = True
        self.number_of_trades = self.number_of_trades + 1
        self.option_entry_instrument = None
        target_points = 270 if "BANK" in self.instrument.tradingsymbol else 90
        sl_points = 300 if "BANK" in self.instrument.tradingsymbol else 100
        if reversal:
            sl_points = abs(entry_candle["close"] - entry_candle["high"]) if side == "SELL" else abs(
                entry_candle["close"] - entry_candle["low"])
        remarks = {"target_points": target_points,
                   "sl_points": sl_points,
                   "target_price": target_points + entry_candle["close"] if side == "BUY" else entry_candle[
                                                                                                   "close"] - target_points,
                   "sl_price": entry_candle["close"] - sl_points if side == "BUY" else entry_candle[
                                                                                           "close"] + sl_points,
                   "vwap_reversal": self.entry_condition["vwap_reversal"] == "vwap_reversal" and not reversal}

        if self.order_type != "OPTIONS_ONLY":
            self.add_info_user_message(
                f"Placing entry order for {self.order_instrument} {side} {self.order_quantity} {identifier}")
            self.add_info_user_message(f"Entry remarks for {self.order_instrument} are {remarks}")
            # Futures order
            self.place_market_order(instrument=self.order_instrument, side=side,
                                    quantity=self.order_quantity, type="NRML", identifer=identifier,
                                    remarks=json.dumps(remarks), price=entry_candle["close"],
                                    instrument_identifier=self.instrument.tradingsymbol)
        # Options order
        if self.order_type != "FUTURES_ONLY":
            if entry_candle["close"] % 100 < 50:
                targeted_strike_price = entry_candle["close"] - entry_candle["close"] % 100
            else:
                targeted_strike_price = entry_candle["close"] + (100 - entry_candle["close"] % 100)
            if side == "BUY":
                option_intruments = InstrumentManager.get_instance().get_call_options_for_instrument(
                    "BANKNIFTY" if "BANK" in self.instrument.tradingsymbol else "NIFTY", strike=targeted_strike_price)
            else:
                option_intruments = InstrumentManager.get_instance().get_put_options_for_instrument(
                    "BANKNIFTY" if "BANK" in self.instrument.tradingsymbol else "NIFTY",
                    strike=targeted_strike_price)
            for optioninstr in option_intruments:
                if str(optioninstr.expiry) == self.option_expiry:
                    self.option_entry_instrument = optioninstr
                    break
            if self.option_entry_instrument:
                self.add_info_user_message(
                    f"Placing entry order for {self.option_entry_instrument} BUY {self.option_quantity} {identifier}")

                self.place_market_order(instrument=self.option_entry_instrument, side="BUY",
                                        quantity=self.option_quantity, type="NRML", identifer=identifier,
                                        price=entry_candle["close"],
                                        remarks=json.dumps(remarks),
                                        instrument_identifier=self.instrument.tradingsymbol)
            else:
                self.add_info_user_message(
                    f"Option entry not found for {targeted_strike_price} {self.instrument.tradingsymbol}")
        self.add_open_positions()

    def place_exit_order(self, instrument, quantity, side, price, identifier=None):
        if self.state == StrategyState.STOPPED:
            return
        self.entry = False
        # if self.order_type != "OPTIONS_ONLY":
        self.add_info_user_message(
            f"Placing exit order for {self.order_instrument} {side} {quantity} {identifier}")
        self.place_market_order(instrument=instrument,
                                side=side, quantity=quantity, price=price,
                                type="NRML", identifer=identifier)
        # if self.order_type != "FUTURES_ONLY" and self.option_entry_instrument:
        #     self.add_info_user_message(
        #         f"Placing exit order for {instrument} SELL {quantity} {identifier}")
        #     self.place_market_order(instrument=instrument,
        #                                    side="SELL", quantity=self.option_quantity,
        #                                    type="NRML", identifer=identifier, price=price)

    def _initiate_inputs(self, inputs):
        print(inputs["instrument"])
        self.instrument = Instrument(symbol=inputs["instrument"])
        self.order_instrument = Instrument(symbol=inputs["order_instrument"])
        self.option_side = inputs["option_side"]
        self.option_quantity = inputs["option_quantity"]
        self.order_quantity = int(inputs["order_quantity"])
        self.option_expiry = inputs["option_expiry"]
        self.order_type = inputs["orders_type"]

    def _initialize_indicators(self):
        self.param_indicator = ParamIndicator(instrument=self.instrument, timeframe=CandleInterval.fifteen_min)
        self.stochastic = Stochastic(instrument=self.instrument,
                                     timeframe=CandleInterval.fifteen_min,
                                     k_length=5,
                                     k_smooth=3,
                                     d_smooth=3)
        from_date = datetime.now() - timedelta(days=7)
        to_date = datetime.now() - timedelta(hours=6)
        interval = CandleInterval.day
        indicator_values = PivotIndicator().calculate(instrument=self.instrument, from_date=from_date, to_date=to_date,
                                                      interval=interval)
        self.yesterdays_pivot_points = indicator_values[-1]
        yesterdays_date = indicator_values[-1]["date"]
        self.add_info_user_message(f"Yesterdays pivot points {self.yesterdays_pivot_points}")
        self.pivot_points = indicator_values[-1]
        from_date = datetime.now() - timedelta(days=5)
        to_date = datetime.now()
        yesterdays_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                               from_date=from_date, to_date=to_date,
                                                                               interval=CandleInterval.fifteen_min)
        last_candle = None
        for data in yesterdays_data:
            if data['date'].date() == yesterdays_date.date():
                last_candle = data
        yesterdays_candle = last_candle
        self.yesterdays_choppy_range = self._check_pivot(yesterdays_candle, pivot=self.yesterdays_pivot_points)
        self.vwap_indicator = VolumeWeightedAveragePrice(instrument=self.instrument,
                                                         interval=CandleInterval.fifteen_min)
        print(f"VWAP Value is {self.vwap_indicator.vwap_value}")

    def on_create(self, inputs):
        logging.info("Adding test log")
        input_file = inputs['input_file']
        input_df = None
        if input_file.endswith('.csv'):
            input_df = pd.read_csv(input_file)
        elif input_file.endswith('.xlsx'):
            input_df = pd.read_excel(input_file)
        conditions = input_df.to_dict('records')
        self.conditions = conditions
        self._initiate_inputs(inputs)
        self._initialize_indicators()
        self.add_open_positions()
        self.subscribe(self.instrument, self.on_ticks)
        self.entry = False
        self.todays_candle_high = None
        self.todays_candle_low = None
        # self.place_entry_order("BUY", 100.2)

    def define_inputs(self):
        order_instruments = InstrumentManager.get_instance().get_futures_for_instrument(symbol="NIFTY")
        order_instruments.extend(InstrumentManager.get_instance().get_futures_for_instrument(symbol="BANKNIFTY"))
        order_instruments = sorted(order_instruments, key=lambda instrument: instrument.expiry)
        order_instrument_names = [instrument.tradingsymbol for instrument in order_instruments]
        option_intruments = InstrumentManager.get_instance().get_call_options_for_instrument(
            "BANKNIFTY")
        expiries = sorted(set(str(instrument.expiry) for instrument in option_intruments))
        return {
            "instrument": order_instrument_names,
            "orders_type": ["FUTURE_AND_OPTIONS", "FUTURES_ONLY", "OPTIONS_ONLY"],
            "order_instrument": order_instrument_names,
            "order_quantity": "50",
            "option_quantity": "50",
            "option_side": ["BUY"],
            "option_expiry": list(expiries),
            "input_file": ["resources/eighteen_banknifty.csv", "resources/eighteen_nifty.csv"],
        }

    def on_ticks(self, tick):
        try:
            if self.state == StrategyState.STOPPED:
                return
            if tick.symbol != self.instrument.tradingsymbol:
                return
            squared_off_positions = []
            for position in self.open_positions:
                entry_side = position.side
                target_price = json.loads(position.remarks)["target_price"]
                # Calculating targets
                LOGGER.info(f"Calculating exit for {position.instrument} with local vars {locals()}")
                if entry_side == "BUY" and tick.ltp >= target_price:
                    position.is_squared = True
                    position.save()
                    squared_off_positions.append(position)
                    self.place_exit_order(Instrument(str(position.instrument)), position.quantity, "SELL", tick.ltp,
                                          TradeIdentifier.TARGET_TRIGGERED)
                if entry_side == "SELL" and tick.ltp <= target_price:
                    position.is_squared = True
                    position.save()
                    squared_off_positions.append(position)
                    self.place_exit_order(Instrument(str(position.instrument)), position.quantity, "BUY", tick.ltp,
                                          TradeIdentifier.TARGET_TRIGGERED)
            for position in squared_off_positions:
                self.open_positions.remove(position)
        except Exception as e:
            LOGGER.exception(e)

    def calculate_exits_for_current_positions(self):
        from_date = datetime.now() - timedelta(minutes=30)
        to_date = datetime.now()
        recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                           from_date=from_date,
                                                                           to_date=to_date,
                                                                           interval=CandleInterval.fifteen_min)
        close = recent_data[-1]["close"] if len(recent_data) > 0 else None
        if close:
            squared_off_positions = []
            for position in self.open_positions:
                entry_side = position.side
                sl_price = json.loads(position.remarks)["sl_price"]
                vwap_reversal = json.loads(position.remarks)["vwap_reversal"]
                # Calculating stoplosses
                if entry_side == "BUY" and close <= sl_price:
                    position.is_squared = True
                    position.save()
                    squared_off_positions.append(position)
                    self.place_exit_order(Instrument(str(position.instrument)), position.quantity, "SELL", close,
                                          TradeIdentifier.STOP_LOSS_TRIGGERED)
                if entry_side == "SELL" and close >= sl_price:
                    position.is_squared = True
                    position.save()
                    squared_off_positions.append(position)
                    self.place_exit_order(Instrument(str(position.instrument)), position.quantity, "BUY", close,
                                          TradeIdentifier.STOP_LOSS_TRIGGERED)
                if vwap_reversal and entry_side == "SELL" and close > self.vwap_value:
                    self.add_info_user_message(
                        f"VWAP Reversal since {close} greater than {self.vwap_value} for position {position.instrument}")
                    position.is_squared = True
                    position.save()
                    squared_off_positions.append(position)
                    self.place_exit_order(Instrument(str(position.instrument)), position.quantity, "BUY", close,
                                          TradeIdentifier.TRADE_REVERSAL)
                    self.place_entry_order("BUY", recent_data[-1], TradeIdentifier.ENTRY, True)
                    pass
                if vwap_reversal and entry_side == "BUY" and close < self.vwap_value:
                    self.add_info_user_message(
                        f"VWAP Reversal since {close} lesser than {self.vwap_value} for position {position.instrument}")
                    position.is_squared = True
                    position.save()
                    squared_off_positions.append(position)
                    self.place_exit_order(Instrument(str(position.instrument)), position.quantity, "SELL", close,
                                          TradeIdentifier.TRADE_REVERSAL)
                    self.place_entry_order("SELL", recent_data[-1], TradeIdentifier.ENTRY, True)

            for position in squared_off_positions:
                self.open_positions.remove(position)

    def update_indicators(self):
        from_date = datetime.now() - timedelta(hours=1)
        to_date = datetime.now()
        recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                           from_date=from_date,
                                                                           to_date=to_date,
                                                                           interval=CandleInterval.fifteen_min)
        self.stochastic_value = self.stochastic.calculate(candle=recent_data[-1])
        self.param_indicator_value = self.param_indicator.calculate(candle=recent_data[-1])
        self.vwap_indicator.calculate(candle=recent_data[-1])
        self.vwap_value = self.vwap_indicator.vwap_value

    def calculate_entries(self):
        if self.last_calculated_entry and datetime.now().replace(second=0, microsecond=0) == self.last_calculated_entry:
            return
        if self.entry:
            return
        self.last_calculated_entry = datetime.now().replace(second=0, microsecond=0)
        from_date = datetime.now() - timedelta(hours=1)
        to_date = datetime.now()
        recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                           from_date=from_date,
                                                                           to_date=to_date,
                                                                           interval=CandleInterval.fifteen_min)
        bullish_bearish = 'bullish' if recent_data[-1]['close'] > recent_data[-1]['open'] else 'bearish'
        LOGGER.info(f"Calculating entry for {self.instrument.tradingsymbol} with local vars {locals()} ")
        if recent_data[-1]["close"] >= self.todays_candle_high or recent_data[-1]["close"] <= self.todays_candle_low:
            self.add_info_user_message(
                f"Todays Levels broken for candle {recent_data[-1]['date']} with close {recent_data[-1]['close']} Calculating entries")
            self.add_info_user_message(
                f"System param {self.param_indicator_value} candle {bullish_bearish} level {self._check_pivot(recent_data[-1], self.yesterdays_pivot_points)} stoch {self.stochastic.signal}")
            for condition in self.conditions:
                if condition["para"] == self.param_indicator_value \
                        and condition["candle"] == bullish_bearish \
                        and condition["level"] == self._check_pivot(recent_data[-1], self.yesterdays_pivot_points) \
                        and condition["stoch"] == self.stochastic.signal:
                    self.add_info_user_message(f"Entry Condition {condition} ")
                    if condition["signal"].upper() not in ("BUY", "SELL"):
                        continue
                    self.entry_condition = condition
                    self.place_entry_order(condition["signal"].upper(), recent_data[-1], TradeIdentifier.ENTRY)
        else:
            self.add_info_user_message(
                f"Levels {self.todays_candle_low} - {self.todays_candle_high}  not broken yet for close {recent_data[-1]['close']} {self.instrument.tradingsymbol} {recent_data[-1]['date']}")
            self.add_info_user_message(
                f"System param {self.param_indicator_value} candle {bullish_bearish} level {self._check_pivot(recent_data[-1], self.yesterdays_pivot_points)} stoch {self.stochastic.signal}")

    def calculate_triggers(self):
        try:
            if self.state == StrategyState.STOPPED:
                return
            now = datetime.now()
            # if now.hour == 3 and now.minute==15 and self.entry:
            #     self.place_exit_order("BUY" if self.entry_side=="SELL" else "SELL", TradeIdentifier.DAY_END_SQUARE_OFF)
            # TODO MOD 15
            expected_timing = datetime.now().replace(hour=10, minute=45, second=0, microsecond=0)
            if now.minute % 15 == 0:
                # if now.minute % 1 == 0:
                LOGGER.info(f"Calculating triggers for current time {now}")
                self.calculate_exits_for_current_positions()
                self.update_indicators()
                if now > expected_timing and self.todays_candle_high and self.todays_candle_low \
                        and not (now.hour >= 3 and now.minute >= 15):
                    self.calculate_entries()

            if not self.todays_candle_high and not self.todays_candle_low:
                # TODO Refactor this for proper condition on 10:45

                if now < expected_timing:
                    LOGGER.info(f"Now {now} is lesser than expected timing {expected_timing}")
                    return

                LOGGER.info("Im here calculating todays candle high")
                # TODO remove timedelta from from_date and to_date
                from_date = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
                to_date = datetime.now().replace(hour=10, minute=30, second=0, microsecond=0)
                recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                                   from_date=from_date,
                                                                                   to_date=to_date,
                                                                                   interval=CandleInterval.fifteen_min)

                LOGGER.info(f"Historical data to calculate candle for today is {recent_data}")
                self.todays_candle_high = max(recent_data[-1]["high"], recent_data[-2]["high"], recent_data[-3]["high"],
                                              recent_data[-4]["high"], recent_data[-5]["high"], recent_data[-6]["high"])
                self.todays_candle_low = min(recent_data[-1]["low"], recent_data[-2]["low"], recent_data[-3]["low"],
                                             recent_data[-4]["low"], recent_data[-5]["low"], recent_data[-6]["low"])
                self.add_info_user_message(
                    f"Todays 9:15-10:45 candle high:{self.todays_candle_high} low:{self.todays_candle_low}")


        except Exception as e:
            LOGGER.info(traceback.format_exc())
            self.add_info_user_message(f"Failure occured while calculating triggers {e} stopping strategy")
            self.stop()
            LOGGER.exception(f"Exception occured for calculate_triggers for {self.inputs}", e)
            raise e

    def schedule_tasks(self):
        schedule.every(1).seconds.do(self.calculate_triggers)

    def stop(self):
        # if self.entry and self.entry_side == "BUY":
        #     self.place_exit_order("SELL", "STOP_SQUARE_OFF")
        # if self.entry and self.entry_side == "SELL":
        #     self.place_exit_order("BUY", "STOP_SQUARE_OFF")
        super().stop()

    def add_open_positions(self):
        from AlgoApp.models import StrategyOrderHistory
        last_orders = StrategyOrderHistory.objects.filter(instrument_identifier=self.instrument.tradingsymbol,
                                                          strategy=self.strategy_name,
                                                          broker=self.inputs["broker_alias"], is_squared=False)
        for last_order in last_orders:
            if last_order and last_order.identifier == TradeIdentifier.ENTRY.name:
                self.open_positions.append(last_order)
                self.add_info_user_message(
                    f"Open position for {self.instrument.tradingsymbol} {self.inputs['broker_alias']} {last_order.side} added ")

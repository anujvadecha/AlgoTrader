import json
import logging
import traceback
from datetime import datetime, timedelta

import pandas as pd
import schedule

from Core.Enums import CandleInterval, StrategyState, TradeIdentifier
from Core.Strategy import Strategy
from Indicators.PivotIndicator import PivotIndicator
from Indicators.atr import AverageTrueRange
from Indicators.psar import ParabolicSAR
from Indicators.stoch import Stochastic
from Indicators.supertrend import SuperTrend
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Models.Models import Instrument

LOGGER = logging.getLogger(__name__)


class Viral_ATR(Strategy):
    strategy_name = "ViralATR"
    trade_limit = 1
    number_of_trades = 0
    last_calculated_entry = None
    def __init__(self):
        self.target_price = None
        self.stoploss_price = None
        self.entry_side = None
        self.entry_price = None
        self.PSAR = None
        self.ATR = None
        self.ST = None

        self.can_trade = None
        self.pivot_points = None
        self.Stoch = None
        self.trade_dir = None
        self.option_entry_instrument = None
        self.entry = None
        super().__init__()

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

    def place_entry_order(self, side, identifier=TradeIdentifier.ENTRY):

        self.entry = True
        self.number_of_trades = self.number_of_trades + 1
        self.option_entry_instrument = None
        if self.order_type != "OPTIONS_ONLY":
            self.add_info_user_message(
                f"Placing entry order for {self.order_instrument} {side} {self.order_quantity} {identifier}")
            # Futures order
            self.place_market_order(instrument=self.order_instrument, side=side,
                                    quantity=self.order_quantity, type="NRML")
        # Options order
        if self.order_type != "FUTURES_ONLY":
            if self.entry_price % 100 < 50:
                targeted_strike_price = self.entry_price - self.entry_price % 100
            else:
                targeted_strike_price = self.entry_price + (100 - self.entry_price % 100)
            if side == "BUY":
                option_intruments = InstrumentManager.get_instance().get_call_options_for_instrument(
                    "BANKNIFTY" if self.spot_instrument.tradingsymbol == "NIFTY BANK" else "NIFTY",
                    strike=targeted_strike_price)
            else:
                option_intruments = InstrumentManager.get_instance().get_put_options_for_instrument(
                    "BANKNIFTY" if self.spot_instrument.tradingsymbol == "NIFTY BANK" else "NIFTY",
                    strike=targeted_strike_price)
            for optioninstr in option_intruments:
                if str(optioninstr.expiry) == self.option_expiry:
                    self.option_entry_instrument = optioninstr
                    break
            if self.option_entry_instrument:
                self.add_info_user_message(
                    f"Placing entry order for {self.option_entry_instrument} BUY {self.option_quantity} {identifier}")

                self.place_market_order(instrument=self.option_entry_instrument, side="BUY",
                                        quantity=self.option_quantity, type="NRML")
            else:
                self.add_info_user_message(
                    f"Option entry not found for {targeted_strike_price} {self.instrument.tradingsymbol}")

            saved_dict = {"overnight": True,
                          "entry_side": self.entry_side,
                          "entry_price": self.entry_price,
                          "stoploss": self.stoploss_price,
                          "target": self.target_price,
                          "option_entry_instrument": self.option_entry_instrument.tradingsymbol,
                          "order_instrument": self.order_instrument.tradingsymbol,
                          "option_quantity": self.option_quantity,
                          "order_quantity": self.order_quantity}

            with open(self.trade_file_name, 'w') as file:
                file.write(json.dumps(saved_dict))

    def place_exit_order(self, side, identifier=None):
        if self.state == StrategyState.STOPPED:
            return
        self.entry = False
        if self.order_type != "OPTIONS_ONLY":
            self.add_info_user_message(
                f"Placing exit order for {self.order_instrument} {side} {self.order_quantity} {identifier}")
            self.place_market_order(instrument=self.order_instrument,
                                    side=side, quantity=self.order_quantity,
                                    type="NRML")
        if self.order_type != "FUTURES_ONLY" and self.option_entry_instrument:
            self.add_info_user_message(
                f"Placing exit order for {self.option_entry_instrument} SELL {self.option_quantity} {identifier}")
            self.place_market_order(instrument=self.option_entry_instrument,
                                    side="SELL", quantity=self.option_quantity,
                                    type="NRML")
        with open(self.trade_file_name, 'r') as file:
            data = file.read()
        saved_dict = json.loads(data)
        saved_dict["overnight"] = False
        with open(self.trade_file_name, 'w') as file:
            file.write(json.dumps(saved_dict))

    def define_inputs(self):
        order_instruments = InstrumentManager.get_instance().get_futures_for_instrument(symbol="NIFTY")
        order_instruments.extend(InstrumentManager.get_instance().get_futures_for_instrument(symbol="BANKNIFTY"))
        order_instrument_names = [instrument.tradingsymbol for instrument in order_instruments]
        option_instruments = InstrumentManager.get_instance().get_call_options_for_instrument(
            "BANKNIFTY")
        expiries = sorted(set(str(instrument.expiry) for instrument in option_instruments))
        # instruments = ["NIFTY 50", "NIFTY BANK"]
        instruments = order_instrument_names
        timeframes = ["hourly"]
        return {
            "instrument": instruments,
            "timeframe": timeframes,
            "orders_type": ["FUTURE_AND_OPTIONS", "FUTURES_ONLY", "OPTIONS_ONLY"],
            "order_instrument": order_instrument_names,
            "order_quantity": "50",
            "option_quantity": "50",
            "option_side": ["BUY"],
            "option_expiry": list(expiries),
        }

    def _initiate_inputs(self, inputs):
        order_instrument = None
        # if inputs["instrument"] == "NIFTY 50":
        #     order_instruments = InstrumentManager.get_instance().get_futures_for_instrument(symbol="NIFTY")
        # else:
        #     order_instruments = InstrumentManager.get_instance().get_futures_for_instrument(symbol="BANKNIFTY")
        # expiries = list(sorted(set(str(instrument.expiry) for instrument in order_instruments)))
        # # TODO find better method
        # if order_instruments is None:
        #     self.add_info_user_message('no order instrument')
        # for instrument in order_instruments:
        #     if instrument.expiry == expiries[0]:
        #         print("matched")
        #         break
        # print(expiries)
        # self.instrument = inputs["instrument"]
        # print(self.instrument.tradingsymbol)
        if "BANK" in inputs["instrument"]:
            self.spot_instrument = Instrument(symbol="NIFTY BANK")
        else:
            self.spot_instrument = Instrument(symbol="NIFTY 50")
        self.instrument = Instrument(symbol=inputs["instrument"])
        self.order_instrument = Instrument(symbol=inputs["order_instrument"])
        self.order_type = inputs["orders_type"]
        self.option_side = inputs["option_side"]
        self.option_quantity = inputs["option_quantity"]
        self.order_quantity = int(inputs["order_quantity"])
        self.option_expiry = inputs["option_expiry"]
        self.interval = CandleInterval.hourly

    def on_create(self, inputs):
        self._initiate_inputs(inputs)

        input_file = None
        if "BANK" in inputs["instrument"]:
            input_file = "resources/ATR_BNF_disc.csv"
        else:
            input_file = "resources/ATR_NF_disc.csv"

        input_df = None
        if input_file.endswith('.csv'):
            input_df = pd.read_csv(input_file)
        elif input_file.endswith('.xlsx'):
            input_df = pd.read_excel(input_file)
        self.trade_dir = input_df.to_dict('records')

        interval = CandleInterval.day
        from_date = datetime.now() - timedelta(days=7)
        to_date = datetime.now() - timedelta(hours=6)
        indicator_values = PivotIndicator().calculate(instrument=self.instrument,
                                                      from_date=from_date,
                                                      to_date=to_date,
                                                      interval=interval)
        self.pivot_points = indicator_values[-1]
        self.add_info_user_message(f"Pivot points {self.pivot_points}")

        self.ATR = AverageTrueRange(instrument=self.instrument,
                                    timeframe=self.interval,
                                    length=14)
        self.PSAR = ParabolicSAR(instrument=self.instrument,
                                 timeframe=self.interval,
                                 start=0.02,
                                 increment_step=0.02,
                                 inc_max=0.2)
        self.ST = SuperTrend(instrument=self.instrument,
                             timeframe=self.interval,
                             atr_length=10,
                             factor=3)

        self.Stoch = Stochastic(instrument=self.instrument,
                                timeframe=self.interval,
                                k_length=5,
                                k_smooth=3,
                                d_smooth=3)

        self.can_trade = {"param1": {'bullish': True, 'bearish': True},
                          "param2": {'bullish': True, 'bearish': True},
                          "param3": {'bullish': True, 'bearish': True},
                          "param4": {'bullish': True, 'bearish': True},
                          "param1 alt": {'bullish': True, 'bearish': True},
                          "param2 alt": {'bullish': True, 'bearish': True},
                          "param3 alt": {'bullish': True, 'bearish': True},
                          "param4 alt": {'bullish': True, 'bearish': True}}

        if self.spot_instrument == "NIFTY 50":
            self.trade_file_name = "resources/atr_nf_trade.txt"
        else:
            self.trade_file_name = "resources/atr_bnf_trade.txt"

        with open(self.trade_file_name, 'r') as file:
            data = file.read()

        # prev_trade = json.loads(data)
        # if prev_trade['overnight']:
        #     self.add_info_user_message('found overnight trade')
        #     self.entry = True
        #     self.target_price = prev_trade["target"]
        #     self.stoploss_price = prev_trade["stoploss"]
        #     self.option_entry_instrument = Instrument(symbol=["option_entry_instrument"])
        #     self.entry_side = prev_trade["entry_side"]
        #     self.order_quantity = prev_trade["order_quantity"]
        #     self.option_quantity = prev_trade["option_quantity"]

        self.subscribe(self.instrument, self.on_ticks)
        self.add_info_user_message("Started ATR for symbol " + inputs["instrument"])

    def calculate_triggers(self):
        try:
            if self.state == StrategyState.STOPPED:
                return
            now = datetime.now()

            if now.minute == 15:
                if now.hour == 9 and now.minute == 15:
                    return
                if self.last_calculated_entry and datetime.now().replace(second=0,
                                                                         microsecond=0) == self.last_calculated_entry:
                    return
                self.last_calculated_entry = datetime.now().replace(second=0, microsecond=0)
                # update indicators
                from_date = datetime.now() - timedelta(hours=6)
                to_date = datetime.now()
                recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                                   from_date=from_date,
                                                                                   to_date=to_date,
                                                                                   interval=self.interval)
                candle = recent_data[-1]
                # update indicators
                self.ATR.calculate(candle=candle)
                self.PSAR.calculate(candle=candle)
                self.ST.calculate(candle=candle)
                self.Stoch.calculate(candle=candle)

                # get required values
                atr = self.ATR.ATR
                psar = self.PSAR.trend
                st = self.ST.trend
                stoch = self.Stoch.signal
                candle_size = abs(candle["open"] - candle["close"])
                candle_type = "bearish" if candle["open"] > candle["close"] else "bullish"
                pivot_range = self._check_pivot(candle, pivot=self.pivot_points)

                self.add_info_user_message(f"atr: {atr}")
                self.add_info_user_message(f"psar: {psar}")
                self.add_info_user_message(f"st: {st}")
                self.add_info_user_message(f"stoch: {stoch}")
                self.add_info_user_message(f"pivot_range: {pivot_range}")
                self.add_info_user_message(f"candle_size: {candle_size}")

                # calculate parameter
                param = ""
                # parameter determinations
                if psar > 0 and st > 0:
                    # PSAR buy ST buy
                    if atr < candle_size:
                        param = "param1"
                elif psar < 0 and st > 0:
                    # PSAR sell ST buy
                    if atr < candle_size:
                        param = "param2"
                elif psar > 0 and st < 0:
                    # PSAR buy ST sell
                    if atr < candle_size:
                        param = "param3"
                elif psar < 0 and st < 0:
                    # PSAR sell ST sell
                    if atr < candle_size:
                        param = "param4"

                if param == "":
                    return

                # alternate condition check
                alt = " alt" if candle_size > (atr * 2.00) else ""

                final_param = param + alt

                if not self.can_trade[final_param][candle_type]:
                    return
                self.add_info_user_message(f'param {final_param}')

                trade_type = None
                for dec in self.trade_dir:
                    if dec['param'] == final_param:
                        if dec['candle'] == candle_type:
                            if dec['stoch'] == stoch:
                                if dec['pivot'] == pivot_range:
                                    trade_type = (dec['decision'])
                                    break
                self.add_info_user_message(f'decision {trade_type}')
                if trade_type == "no_trade":
                    return

                self.can_trade[final_param][candle_type] = False

                # execute entry
                data = MarketDataManager.get_instance().get_historical_data(instrument=self.spot_instrument,
                                                                            from_date=from_date,
                                                                            to_date=to_date,
                                                                            interval=self.interval)[-1]
                self.entry_price = data['close']
                self.entry_side = trade_type.upper()
                self.stoploss_price = 0.00
                self.target_price = 0.00
                if "alt" in final_param:
                    if self.entry_side == "BUY":
                        self.stoploss_price = round(candle["close"] - (atr * 1.5), 2)
                        self.target_price = round(
                            candle["close"] + (atr * 1.5), 2)
                        self.place_entry_order("BUY")
                    elif self.entry_side == "SELL":
                        self.stoploss_price = round(
                            candle["close"] + (atr * 1.5), 2)
                        self.target_price = round(
                            candle["close"] - (atr * 1.5), 2)
                        self.place_entry_order("SELL")
                else:
                    if self.entry_side == "BUY":
                        self.stoploss_price = round(
                            candle["close"] - atr, 2)
                        self.target_price = round(
                            candle["close"] + atr, 2)
                        self.place_entry_order("BUY")
                    elif self.entry_side == "SELL":
                        self.stoploss_price = round(
                            candle["close"] + atr, 2)
                        self.target_price = round(
                            candle["close"] - atr, 2)
                        self.place_entry_order("SELL")

                self.entry = True

        except Exception as e:
            LOGGER.info(traceback.format_exc())
            self.add_info_user_message(f"Failure occurred while calculating triggers {e} stopping strategy")
            self.stop()
            LOGGER.exception(f"Exception occurred for calculate_triggers for {self.inputs}", e)
            raise e

    def on_ticks(self, tick):
        try:
            if tick.symbol == self.instrument.tradingsymbol and self.entry:
                if self.entry_side == "BUY":
                    if tick.ltp >= self.target_price:
                        self.place_exit_order("SELL", TradeIdentifier.TARGET_TRIGGERED)

                    if tick.ltp <= self.stoploss_price:
                        self.place_exit_order("SELL", TradeIdentifier.STOP_LOSS_TRIGGERED)

                if self.entry_side == "SELL":
                    if tick.ltp <= self.target_price:
                        self.place_exit_order("BUY", TradeIdentifier.TARGET_TRIGGERED)

                    if tick.ltp >= self.stoploss_price:
                        self.place_exit_order("BUY", TradeIdentifier.STOP_LOSS_TRIGGERED)
        except Exception as e:
            LOGGER.exception(e)

    def schedule_tasks(self):
        schedule.every(1).seconds.do(self.calculate_triggers)

    def stop(self):
        if self.entry and self.entry_side == "BUY":
            self.place_exit_order("SELL", TradeIdentifier.STOP_SQUARE_OFF)
        if self.entry and self.entry_side == "SELL":
            self.place_exit_order("BUY", TradeIdentifier.STOP_SQUARE_OFF)
        super().stop()

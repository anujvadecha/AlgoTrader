from datetime import datetime, timedelta
import enum
import pytz
import schedule
import pandas as pd
from dateutil.tz import tzoffset
from Indicators.PivotIndicator import PivotIndicator
from Managers.InstrumentManager import InstrumentManager
from Core.Strategy import Strategy
from Managers.MarketDataManager import MarketDataManager
from Models.Models import Instrument



class ChoppyRanges(enum.Enum):
    greater_r3 = ">r3"
    r3_r2 = "r3-r2"
    r2_pdh  = "r2-pdh"
    r2_r1 = "r2-r1"
    pdh_r1 = "pdh-r1"
    r1_pdh = "r1-pdh"
    r1_tc = "r1-tc"
    pdh_tc = "pdh-tc"
    tc_pp = "tc-pp"
    pp_bc = "pp-bc"
    bc_pdl = "bc-pdl"
    bc_s1 = "bc-s1"
    pdl_s1 = "pdl-s1"
    s1_pdl = "s1-pdl"
    pdl_s2 = "pdl-s2"
    s1_s2 = "sl-s2"
    s2_s3 = "s2-s3"
    less_s3 = "<s3"


class Choppy(Strategy):

    def _check_pivot(self, candle, pivot):
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
        return ChoppyRanges(pivot_range)

    def _calculate_choppy_range(self, candle, pivot_points):
        candle_close = candle["close"]
        if candle_close >= pivot_points["r3"]:
            return ChoppyRanges.greater_r3
        elif candle_close <= pivot_points["r3"] and candle_close >= pivot_points["r2"]:
            return ChoppyRanges.r3_r2
        elif candle_close <= pivot_points["r2"] and candle_close >= pivot_points["pdh"]:
            return ChoppyRanges.r2_pdh
        elif candle_close <= pivot_points["r2"] and candle_close >= pivot_points["r1"]:
            return ChoppyRanges.r2_r1
        elif candle_close <= pivot_points["r1"] and candle_close >= pivot_points["tc"]:
            return ChoppyRanges.r1_tc
        elif candle_close <= pivot_points["r1"] and candle_close >= pivot_points["pdh"]:
            return ChoppyRanges.r1_pdh
        elif candle_close <= pivot_points["pdh"] and candle_close >= pivot_points["r1"]:
            return ChoppyRanges.pdh_r1
        elif candle_close <= pivot_points["pdh"] and candle_close >= pivot_points["tc"]:
            return ChoppyRanges.pdh_tc
        elif candle_close <= pivot_points["tc"] and candle_close >= pivot_points["pp"]:
            return ChoppyRanges.tc_pp
        elif candle_close <= pivot_points["pp"] and candle_close >= pivot_points["bc"]:
            return ChoppyRanges.pp_bc
        elif candle_close <= pivot_points["bc"] and candle_close >= pivot_points["pdl"]:
            return ChoppyRanges.bc_pdl
        elif candle_close <= pivot_points["bc"] and candle_close >= pivot_points["s1"]:
            return ChoppyRanges.bc_s1
        elif candle_close <= pivot_points["pdl"] and candle_close >= pivot_points["s1"]:
            return ChoppyRanges.pdl_s1
        elif candle_close <= pivot_points["s1"] and candle_close >= pivot_points["pdl"]:
            return ChoppyRanges.s1_pdl
        elif candle_close <= pivot_points["pdl"] and candle_close >= pivot_points["s2"]:
            return ChoppyRanges.pdl_s2
        elif candle_close <= pivot_points["s1"] and candle_close >= pivot_points["s2"]:
            return ChoppyRanges.s1_s2
        elif candle_close <= pivot_points["s2"] and candle_close >= pivot_points["s3"]:
            return ChoppyRanges.s2_s3
        elif candle_close <= pivot_points["s3"]:
            return ChoppyRanges.less_s3

    def place_entry_order(self, side):
        self.broker.place_market_order(instrument=self.order_instrument, side=side,
                                       quantity=self.order_quantity, type="CNC")

    def place_exit_order(self, side):
        self.broker.place_market_order(instrument=self.order_instrument,
                                       side=side, quantity=self.order_quantity,
                                       type="CNC")
        self.entry = False


    def on_create(self, inputs):
        input_file = inputs['input_file']
        input_df = None
        if input_file.endswith('.csv'):
            input_df = pd.read_csv(input_file)
        elif input_file.endswith('.xlsx'):
            input_df = pd.read_excel(input_file)
        conditions = input_df.to_dict('records')
        from_date = datetime.now() - timedelta(days=7)
        to_date = datetime.now()
        self.instrument = Instrument(symbol=inputs["instrument"])
        self.order_instrument = Instrument(symbol=inputs["order_instrument"])
        self.order_quantity = int(inputs["order_quantity"])
        interval = "day"
        indicator_values = PivotIndicator().calculate(instrument=self.instrument, from_date=from_date, to_date=to_date, interval=interval)
        self.yesterdays_pivot_points = indicator_values[datetime.now().replace(minute=0, hour=0, second=0, microsecond=0, tzinfo=tzoffset(None, 19800)) - timedelta(days=1)]
        self.messages.usermessages.info(f"Yesterdays pivot points {self.yesterdays_pivot_points}")
        self.pivot_points = indicator_values[datetime.now().replace(minute=0, hour=0, second=0, microsecond=0, tzinfo=tzoffset(None, 19800))]
        from_date = datetime.now() - timedelta(days=3)
        to_date = datetime.now()
        yesterdays_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument, from_date=from_date, to_date=to_date, interval="15minute")
        last_candle = None
        for data in yesterdays_data:
            if data['date'].date() == (datetime.now()- timedelta(days=1)).date():
                last_candle = data
        self.yesterdays_candle = last_candle
        self.yesterdays_choppy_range = self._check_pivot(self.yesterdays_candle, pivot=self.yesterdays_pivot_points)

        valid_conditions = []
        for condition in conditions:
            if condition['yesterdays_candle'] == self.yesterdays_choppy_range.value and condition['script'] == inputs["instrument"]:
                valid_conditions.append(condition)
        self.valid_conditions = valid_conditions
        self.messages.usermessages.info(f"Pivot points {self.pivot_points}")
        self.messages.usermessages.info(f"Yesterdays choppy range is {self.yesterdays_choppy_range.value}")
        self.entry = False
        self.subscribe(self.instrument, self.on_ticks)


    def define_inputs(self):
        return {
            "input_file" : "resources/Choppy_conditions.csv",
            "instrument" : "NIFTY 50",
            "order_instrument": "NIFTY 50",
            "order_quantity": "40"
        }


    def on_ticks(self, tick):
        print("TICKS RECEIVED " + str(tick))
        if tick.symbol==self.instrument.tradingsymbol and self.entry:
            if self.entry_side == "BUY":
                if tick.ltp >= self.target_points:
                    self.place_exit_order("SELL")
            if self.entry_side == "SELL":
                if tick.ltp <= self.target_points:
                    self.place_exit_order("BUY")

    def calculate_triggers(self):
        now = datetime.now()
        if now.minute % 15 == 0:
            # TODO to uncomment
            if not self.entry: #and now.hour == 9 and now.minute == 30:
                print(f"{datetime.now()} calculate triggers called")
                # TODO to change hours to 1
                from_date = datetime.now() - timedelta(hours=6)
                to_date = datetime.now()
                recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                                       from_date=from_date, to_date=to_date,
                                                                                       interval="15minute")
                for data in recent_data:
                    if data['date'].hour==9 and data['date'].minute==15:
                        bullish_bearish = 'bullish' if data['close'] > data['open'] else 'bearish'
                        candle_range = self._check_pivot(data, pivot=self.pivot_points)
                        self.messages.usermessages.info(f"9:15 candle identified {bullish_bearish} with candle range {candle_range.value}")
                        for condition in self.valid_conditions:
                            if condition['todays_candle'] == candle_range.value and condition['candle_type'] == bullish_bearish:
                                if condition['decision']!='no_trade':
                                    if self.entry_price > self.pivot_points["tc"] and self.entry_side == "SELL":
                                        self.target_points = 40
                                    if self.entry_price > self.pivot_points["tc"] and self.entry_side == "BUY":
                                        self.target_points = 60
                                    if self.entry_price < self.pivot_points["bc"] and self.entry_side == "SELL":
                                        self.target_points = 60
                                    if self.entry_price < self.pivot_points["bc"] and self.entry_side == "BUY":
                                        self.target_points = 40
                                    self.messages.usermessages.info(f"Condition {condition} satisfied, triggering order")
                                    self.entry = True
                                    self.place_entry_order(side=condition['decision'].upper())
                                    self.entry_price = data['close']
                                    self.entry_side = condition['decision'].upper()
                                    self.target_price = self.entry_price + self.target_points if self.entry_side=="BUY" else self.entry_price-self.target_points
                                    ranges = candle_range.value.split("-")
                                    upper_range = max(self.pivot_points[range_identifer] for range_identifer in ranges)
                                    lower_range = min(self.pivot_points[range_identifer] for range_identifer in ranges)
                                    self.sl = upper_range if self.entry_side=="SELL" else lower_range
                                    self.messages.usermessages.info(f"Target points{self.target_points} price {self.target_price} side {self.entry_side}")

            if self.entry:
                # Calculating SL exit on 15 minute
                from_date = datetime.now() - timedelta(minutes=30)
                to_date = datetime.now()
                recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                                   from_date=from_date, to_date=to_date,
                                                                                   interval="15minute")
                last_candle = recent_data[-1]
                if self.entry_side =="BUY":
                    if last_candle["close"] <= self.sl:
                        self.place_exit_order("SELL")
                if self.entry_side == "SELL":
                    if last_candle["close"] >= self.sl:
                        self.place_exit_order("BUY")


    def schedule_tasks(self):
        # TODO To change scheduling to something like 10 seconds
        # schedule.every(1).minutes.do(self.calculate_triggers)
        schedule.every(2).seconds.do(self.calculate_triggers)

    def stop(self):
        super().stop()

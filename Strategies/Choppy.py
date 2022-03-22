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

    def _calculate_choppy_range(self, candle):
        candle_close = candle["close"]
        if candle_close >= self.pivot_points["r3"]:
            return ChoppyRanges.greater_r3
        elif candle_close <= self.pivot_points["r3"] and candle_close >= self.pivot_points["r2"]:
            return ChoppyRanges.r3_r2
        elif candle_close <= self.pivot_points["r2"] and candle_close >= self.pivot_points["pdh"]:
            return ChoppyRanges.r2_pdh
        elif candle_close <= self.pivot_points["r2"] and candle_close >= self.pivot_points["r1"]:
            return ChoppyRanges.r2_r1
        elif candle_close <= self.pivot_points["r1"] and candle_close >= self.pivot_points["tc"]:
            return ChoppyRanges.r1_tc
        elif candle_close <= self.pivot_points["r1"] and candle_close >= self.pivot_points["pdh"]:
            return ChoppyRanges.r1_pdh
        elif candle_close <= self.pivot_points["pdh"] and candle_close >= self.pivot_points["r1"]:
            return ChoppyRanges.pdh_r1
        elif candle_close <= self.pivot_points["pdh"] and candle_close >= self.pivot_points["tc"]:
            return ChoppyRanges.pdh_tc
        elif candle_close <= self.pivot_points["tc"] and candle_close >= self.pivot_points["pp"]:
            return ChoppyRanges.tc_pp
        elif candle_close <= self.pivot_points["pp"] and candle_close >= self.pivot_points["bc"]:
            return ChoppyRanges.pp_bc
        elif candle_close <= self.pivot_points["bc"] and candle_close >= self.pivot_points["pdl"]:
            return ChoppyRanges.bc_pdl
        elif candle_close <= self.pivot_points["bc"] and candle_close >= self.pivot_points["s1"]:
            return ChoppyRanges.bc_s1
        elif candle_close <= self.pivot_points["pdl"] and candle_close >= self.pivot_points["s1"]:
            return ChoppyRanges.pdl_s1
        elif candle_close <= self.pivot_points["s1"] and candle_close >= self.pivot_points["pdl"]:
            return ChoppyRanges.s1_pdl
        elif candle_close <= self.pivot_points["pdl"] and candle_close >= self.pivot_points["s2"]:
            return ChoppyRanges.pdl_s2
        elif candle_close <= self.pivot_points["s1"] and candle_close >= self.pivot_points["s2"]:
            return ChoppyRanges.s1_s2
        elif candle_close <= self.pivot_points["s2"] and candle_close >= self.pivot_points["s3"]:
            return ChoppyRanges.s2_s3
        elif candle_close <= self.pivot_points["s3"]:
            return ChoppyRanges.less_s3

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
        self.pivot_points = indicator_values[datetime.now().replace(minute=0, hour=0, second=0, microsecond=0, tzinfo=tzoffset(None, 19800))]
        from_date = datetime.now() - timedelta(days=1)
        to_date = datetime.now()
        yesterdays_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument, from_date=from_date, to_date=to_date, interval="15minute")
        last_candle = None
        for data in yesterdays_data:
            if data['date'].date() == (datetime.now()- timedelta(days=1)).date():
                last_candle = data
        self.yesterdays_candle = last_candle
        self.yesterdays_choppy_range = self._calculate_choppy_range(self.yesterdays_candle)
        valid_conditions = []
        for condition in conditions:
            if condition['yesterdays_candle'] == self.yesterdays_choppy_range.value and condition['script'] == inputs["instrument"]:
                valid_conditions.append(condition)
        self.valid_conditions = valid_conditions
        self.messages.usermessages.info(f"Yesterdays choppy range is {self.yesterdays_choppy_range.value}")
        self.entry = False


    def define_inputs(self):
        return {
            "input_file" : "resources/Choppy_conditions.csv",
            "instrument" : "NIFTY 50",
            "order_instrument": "NIFTY 50",
            "order_quantity": "40"
        }


    def on_ticks(self, ticks):
        print("TICKS RECEIVED " + str(ticks))

    def calculate_triggers(self):
        now = datetime.now()
        # TODO to uncomment
        if not self.entry :#and now.hour == 9 and now.minute == 15:
            print(f"{datetime.now()} calculate triggers called")
            # TODO to change hours to 1
            from_date = datetime.now() - timedelta(hours=32)
            to_date = datetime.now()
            recent_data = MarketDataManager.get_instance().get_historical_data(instrument=self.instrument,
                                                                                   from_date=from_date, to_date=to_date,
                                                                                   interval="15minute")
            for data in recent_data:
                if data['date'].hour==9 and data['date'].minute==15:
                    bullish_bearish = 'bullish' if data['close'] > data['open'] else 'bearish'
                    candle_range = self._calculate_choppy_range(data)
                    self.messages.usermessages.info(f"9:15 candle identified {bullish_bearish} with candle range {candle_range.value}")
                    for condition in self.valid_conditions:
                        if condition['todays_candle'] == candle_range.value and condition['candle_type'] == bullish_bearish:
                            if condition['decision']!='no_trade':
                                self.messages.usermessages.info(f"Condition {condition} satisfied, triggering order")
                                self.entry = True
                                self.broker.place_market_order(instrument=self.order_instrument, side=condition['decision'].upper(), quantity=self.order_quantity, type="CNC")

    def schedule_tasks(self):
        print(f"SCHEDULE TASKS CALLED {self.portfolio_id}")
        # TODO To change scheduling to something like 10 seconds
        # schedule.every(1).minutes.do(self.calculate_triggers)
        schedule.every(2).seconds.do(self.calculate_triggers)

    def stop(self):
        super().stop()

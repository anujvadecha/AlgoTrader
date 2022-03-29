import threading
import time
import datetime
import schedule
# from Managers.BrokerManager import BrokerManager
from Core.Enums import StrategyState
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Managers.OrderManager import OrderManager
# from MessageClasses import Messages
from Models.Models import Instrument, Order
from Core.Strategy import Strategy
import functools
import time
from ATR_Utils.atr_psar import ATR_trigger_start, ATR_trigger_stop


def timer(func):
    """ Print the runtime of the decorated function """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


class ViralATR(Strategy):
    strategy_name = "Viral ATR"

    def define_inputs(self):
        inputs = {
            "input_file": "resources/trade_dis.xlsx"
        }
        return inputs

    def define_attributes(self):
        print("demo strategy define inputs called")
        self.attributes = self.attributes + ['input_file']

    def on_create(self, inputs):
        # self.x = inputs["x"]
        # self.y = inputs["y"]
        print(f"on create for strategy demo called")
        ATR_trigger_start(connection_object=self.broker.get_connection_object(
        ), data_connection_object=self.data_broker.get_connection_object(), ticker_connection_object=self.data_broker.get_ticker_connection(), inputs=inputs, messaging=self.messages)

    def every_second(self):
        print("every second called portfolio "+str(self.portfolio_id)+"  "+str(datetime.datetime.now()))
        self.messages.usermessages.info(
            "every second called portfolio "+str(self.portfolio_id)+"  "+str(datetime.datetime.now()))
        print(self.broker.get_connection_object())
        # order=Order(order_id=1232,status=self.state)
        # Messages.getInstance().orders.addOrder(order)

    def on_ticks(self, ticks):
        print("TICKS RECEIVED " + str(ticks))

    def schedule_tasks(self):
        print(f"SCHEDULE TASKS CALLED {self.portfolio_id}")
        # schedule.every(int(1)).seconds.do(self.every_second)
        # self.subscribe(Instrument(symbol="RELIANCE"), self.on_ticks)

    def stop(self):
        super().stop()
        ATR_trigger_stop()

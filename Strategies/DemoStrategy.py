import threading
import time
import datetime
import schedule
# from Managers.BrokerManager import BrokerManager
from Core.Enums import StrategyState
from Managers.BrokerManager import BrokerManager
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Managers.OrderManager import OrderManager
# from MessageClasses import Messages
from Models.Models import Instrument, Order
from Core.Strategy import Strategy
import functools
import time

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

class DemoStrategy(Strategy):

    def define_inputs(self):
        inputs = {
            "x":5,
            "y":14,
        }
        return inputs

    def define_attributes(self):
        print("demo strategy define inputs called")
        self.attributes = self.attributes + ['inputs', 'x', 'y']

    def on_create(self,inputs):
        self.x = inputs["x"]
        self.y = inputs["y"]
        print(f"on create for strategy demo called")
        self.broker.get_connection_object()
        self.data_broker = BrokerManager.get_instance().get_broker()

    def every_second(self):
        print("every second called portfolio "+str(self.portfolio_id)+"  "+str(datetime.datetime.now()))
        self.messages.usermessages.info("every second called portfolio "+str(self.portfolio_id)+"  "+str(datetime.datetime.now()))
        print(self.broker.get_connection_object())
        # order=Order(order_id=1232,status=self.state)
        # Messages.getInstance().orders.addOrder(order)

    def on_ticks(self, ticks):
        print("TICKS RECEIVED " + str(ticks))

    def schedule_tasks(self):
        print(f"SCHEDULE TASKS CALLED {self.portfolio_id}")
        schedule.every(int(self.x)).seconds.do(self.every_second)
        self.subscribe(Instrument(symbol="RELIANCE"), self.on_ticks)

    def stop(self):
        super().stop()
        print("stop called")


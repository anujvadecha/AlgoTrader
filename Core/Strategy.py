import schedule
import datetime
from Managers.MarketDataManager import MarketDataManager
from Core.Enums import StrategyState
import time




class Strategy():

    portfolio_id = 0
    state = StrategyState.CREATED
    attributes = ['portfolio_id', 'state', 'broker_alias']

    def define_inputs(self):
        return {}

    def define_attributes(self):
        return {}

    def get_attributes(self):
        attr = {}
        for attribute in self.attributes:
             try:
                attr[attribute] = getattr(self, attribute)
             except Exception as e:
                attr[attribute] = ""
        return attr

    def stop(self):
        self.state = StrategyState.STOPPED
        self.messages.running_strategies.update_running_strategy(strategy=self)

    def stop_with_squareoff(self):
        pass

    def pause(self):
        pass

    def pause_with_squareoff(self):
        pass

    def get_total_pnl(self):
        pass

    def get_unrealized_pnl(self):
        pass

    def get_realized_pnl(self):
        pass

    def on_create(self,inputs):
        pass

    def subscribe(self,instrument,callback):
        MarketDataManager.get_instance().subscribe(instrument,callback)

    def schedule_tasks(self):
        pass

    def main(self,inputs):
        from MessageClasses import Messages
        self.messages = Messages.getInstance()
        self.on_create(inputs)
        self.schedule=schedule
        self.schedule_tasks()
        from Managers.BrokerManager import BrokerManager
        self.broker_alias = inputs['broker_alias']
        self.broker = BrokerManager.get_instance().get_broker(broker_alias=inputs['broker_alias'])
        self.data_broker = BrokerManager.get_instance().get_broker()
        self.messages.running_strategies.update_running_strategy(strategy=self)
        self.define_attributes()
        self.state = StrategyState.RUNNING
        self.messages.running_strategies.update_running_strategy(strategy=self)
        while True:
             schedule.run_pending()


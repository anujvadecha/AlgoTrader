import traceback
from enum import Enum

import schedule
import datetime

#
from Managers.MarketDataManager import MarketDataManager
from Core.Enums import StrategyState
import time
import logging
LOGGER = logging.getLogger(__name__)

class Strategy():
    portfolio_id = 0
    strategy_name = ""
    state = StrategyState.CREATED
    attributes = ['portfolio_id', 'strategy_name' ,'state', 'broker_alias', 'inputs']

    def define_inputs(self):
        return {}

    def define_attributes(self):
        return {}

    def get_attributes(self):
        attr = {}
        for attribute in self.attributes:
            try:
                attr[attribute] = getattr(self, attribute)
                if isinstance(attr[attribute], Enum):
                    attr[attribute] =  getattr(self, attribute).value
                if isinstance(attr[attribute], dict):
                    attr[attribute] = ','.join(getattr(self, attribute).values())
            except Exception as e:
                attr[attribute] = ""
                raise e
        return attr

    def stop(self):
        self.state = StrategyState.STOPPED
        self.messages.running_strategies.update_running_strategy(strategy=self)
        self.messages.usermessages.info(f"Stopped Strategy with Portfolio id {self.portfolio_id} ")

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

    def on_create(self, inputs):
        pass

    def subscribe(self, instrument, callback):
        MarketDataManager.get_instance().subscribe(instrument, callback)

    def schedule_tasks(self):
        pass

    def add_info_user_message(self, message):
        self.messages.usermessages.info(message,self.portfolio_id)

    def place_market_order(self, instrument, side, quantity, type="NRML", remarks=None, identifer=None, price=None):
        # TODO ADD orders to db with strategy identifier
        from AlgoApp.models import StrategyOrderHistory
        try:
            StrategyOrderHistory.objects.create(instrument=instrument.tradingsymbol, side=side, quantity=quantity, type=type, portfolio_id=self.portfolio_id, strategy=self.strategy_name, remarks=remarks if remarks else None, identifier=identifer.name if identifer else None, broker=self.inputs["broker_alias"], order_type="MARKET", inputs=self.inputs, price=price if price else None)
        except Exception as e:
            self.add_info_user_message("No Impact Error: creating the entry for trade in database")
            LOGGER.error(f"Error creating StrategyOrderHistory {e}", e)
            LOGGER.info(f"Could not create strategy order due to exception {traceback.format_exc(e)}")
        self.broker.place_market_order(instrument=instrument, side=side, quantity=quantity, type=type)

    def main(self, inputs):
        from MessageClasses import Messages
        self.inputs = inputs
        self.messages = Messages.getInstance()
        self.schedule = schedule
        from Managers.BrokerManager import BrokerManager
        self.broker_alias = inputs['broker_alias']
        self.broker = BrokerManager.get_instance().get_broker(broker_alias=inputs['broker_alias'])
        self.data_broker = BrokerManager.get_instance().get_data_broker()
        self.messages.running_strategies.update_running_strategy(strategy=self)
        self.define_attributes()
        self.state = StrategyState.RUNNING
        self.messages.running_strategies.update_running_strategy(strategy=self)
        try:
            self.on_create(inputs)
            self.schedule_tasks()
        except Exception as e:
            self.messages.usermessages.info(f"Strategy creation failed due to exception {e}")
            self.stop()
            raise e

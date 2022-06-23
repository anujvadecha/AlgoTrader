#
from dataclasses import asdict
from datetime import datetime

from Core.Strategy import Strategy
from Models.Models import UserMessage, BrokerMessage, Order, DisplayOrder


class messagemodel:

    def add(self, message):
        self.messagefactory.append(message)

    def addAll(self, list):
        self.messagefactory.extend(list)

    def reset(self, list):
        self.messagefactory = list

    def getMessages(self):
        if (len(self.messagefactory) == 0):
            return []
        return self.messagefactory

    def __init__(self):
        self.messagefactory = []


class Messages():
    # class Orders(messagemodel):
    #     def addOrder(self, order: Order):
    #         message = DisplayOrder(order_id=order.order_id, order_timestamp=order.order_timestamp,
    #                                status=order.status, tradingsymbol=order.tradingsymbol,
    #                                order_type=order.order_type,
    #                                transaction_type=order.transaction_type, validity=order.validity,
    #                                quantity=order.quantity, price=order.price,
    #                                average_price=order.average_price, filled_quantity=order.filled_quantity,
    #                                pending_quantity=order.pending_quantity
    #                                )
    #         self.messagefactory.append(asdict(message))
    #         from GUIFunctions import GUIFunctions
    #         GUIFunctions.get_instance().add_update_order(asdict(message))
    #
    #
    # class Trades(messagemodel):
    #     def addTrade(self, trade):
    #         pass

    class UserMessages(messagemodel):

        def info(self, message, portfolio_id=''):
            message = UserMessage(datetime.now().strftime('%H:%M:%S'), "INFO", portfolio_id,message)
            self.messagefactory.append(asdict(message))
            from GUIFunctions import GUIFunctions
            GUIFunctions.get_instance().add_user_message(asdict(message))

        def error(self, message, portfolio_id=''):
            message = UserMessage(str(datetime.now().strftime('%H:%M:%S')),"ERROR",portfolio_id , message)
            self.messagefactory.append(asdict(message))
            from GUIFunctions import GUIFunctions
            GUIFunctions.get_instance().add_user_message(asdict(message))

        def warning(self, message, portfolio_id=''):
            message = UserMessage(datetime.now().strftime('%H:%M:%S'),"WARNING",portfolio_id, message)
            self.messagefactory.append(asdict(message))
            from GUIFunctions import GUIFunctions
            GUIFunctions.get_instance().add_user_message(asdict(message))

        # def add(self,type,message):
        #     message=UserMessage(datetime.now().strftime('%H:%M:%S'),type,message)
        #     self.messagefactory.append(asdict(message))
        #     from GUIFunctions import GUIFunctions
        #     GUIFunctions.get_instance().add_user_message(asdict(message))

    class BrokerMessages(messagemodel):
        def info(self, message):
            message = BrokerMessage(datetime.now().strftime('%H:%M:%S'), "INFO", message)
            self.messagefactory.append(asdict(message))
            from GUIFunctions import GUIFunctions
            GUIFunctions.get_instance().add_broker_message(asdict(message))

        def error(self, message):
            message = BrokerMessage(datetime.now().strftime('%H:%M:%S'), "ERROR", message)
            self.messagefactory.append(asdict(message))
            from GUIFunctions import GUIFunctions
            GUIFunctions.get_instance().add_broker_message(asdict(message))

        def warning(self, message):
            message = BrokerMessage(datetime.now().strftime('%H:%M:%S'), "WARNING", message)
            self.messagefactory.append(asdict(message))
            from GUIFunctions import GUIFunctions
            GUIFunctions.get_instance().add_broker_message(asdict(message))

    class RunningStrategies(messagemodel):

        def update_running_strategy(self, strategy: Strategy):
            message = strategy.get_attributes()
            print(message)
            self.messagefactory.append(message)
            from GUIFunctions import GUIFunctions
            GUIFunctions.get_instance().add_update_running_strategy(message)

    # class Positions(messagemodel):
    #     pass

    __instance = None

    @staticmethod
    def getInstance():
        if Messages.__instance == None:
            Messages()
        return Messages.__instance

    def __init__(self):
        if Messages.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Messages.__instance = self
        self.usermessages = self.UserMessages()
        # self.trades = self.Trades()
        # self.orders = self.Orders()
        self.brokermessages = self.BrokerMessages()
        # self.positions = self.Positions()
        self.running_strategies = self.RunningStrategies()

import logging

from PyQt5 import QtCore, QtWidgets

from Managers.BrokerManager import BrokerManager
from Managers.StrategyManager import StrategyManager
from MessageClasses import Messages
from UIElements.StrategyInputs import StrategyInputBox
import os
from config import strategies

LOGGER = logging.getLogger(__name__)

class GUIFunctions():

    def add_update_order(self,order):
        self.populateRunningStrategies()
        root = self.GUI.ordersDisplay.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            order_id = item.text(0)
            if str(order_id) == str(order["order_id"]):
                keys = order.keys()
                for j in range(0,len(keys)):
                    item.setText(j, str(order[keys[j]]))
                return
        if child_count==0:
            self.GUI.ordersDisplay.setHeaderLabels(list(order.keys()))
        item = QtWidgets.QTreeWidgetItem(self.GUI.ordersDisplay)
        for j in range(0, len(list(order.keys()))):
            item.setText(j, str(order[list(order.keys())[j]]))

    def add_update_running_strategy(self,running_strategy):
        root = self.GUI.runningStrategyBox.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            portfolio_id = item.text(0)
            if str(portfolio_id) == str(running_strategy["portfolio_id"]):
                keys = list(running_strategy.keys())
                for j in range(0, len(keys)):
                    item.setText(j, str(running_strategy[keys[j]]))
                return
        if child_count == 0:
            self.GUI.runningStrategyBox.setHeaderLabels(list(running_strategy.keys()))
        item = QtWidgets.QTreeWidgetItem(self.GUI.runningStrategyBox)
        for j in range(0, len(list(running_strategy.keys()))):
            item.setText(j, str(running_strategy[list(running_strategy.keys())[j]]))

    def add_user_message(self,message):
        item = QtWidgets.QTreeWidgetItem(self.GUI.userMessageDisplay)
        for j in range(0, len(list(message.keys()))):
            item.setText(j, str(message[list(message.keys())[j]]))

    def add_broker_message(self,message):
        item = QtWidgets.QTreeWidgetItem(self.GUI.brokerMessagesDisplay)
        for j in range(0, len(list(message.keys()))):
            item.setText(j, str(message[list(message.keys())[j]]))

    def populateUserMessages(self):
        self.GUI.userMessageDisplay.clear()
        usermessages = Messages.getInstance().usermessages.getMessages()
        if (len(usermessages) != 0):
            headers = list(usermessages[0].keys())
            self.GUI.userMessageDisplay.clear()
            self.GUI.userMessageDisplay.setHeaderLabels(headers)
            for i in usermessages:
                item = QtWidgets.QTreeWidgetItem(self.GUI.userMessageDisplay)
                for j in range(0, len(headers)):
                    item.setText(j, str(i[headers[j]]))


    def populateBrokerMessages(self):
        self.GUI.brokerMessagesDisplay.clear()
        brokermessages = Messages.getInstance().brokermessages.getMessages()
        if (len(brokermessages) != 0):
            headers = list(brokermessages[0].keys())
            self.GUI.brokerMessagesDisplay.clear()
            self.GUI.brokerMessagesDisplay.setHeaderLabels(headers)
            for i in brokermessages:
                item = QtWidgets.QTreeWidgetItem(self.GUI.brokerMessagesDisplay)
                for j in range(0, len(headers)):
                    item.setText(j, str(i[headers[j]]))


    def populateOrders(self):
        orders = Messages.getInstance().orders.getMessages()
        self.GUI.ordersDisplay.clear()
        if (len(orders) != 0):
            headers = list(orders[0].keys())
            self.GUI.ordersDisplay.setHeaderLabels(headers)
            for i in orders:
                item = QtWidgets.QTreeWidgetItem(self.GUI.ordersDisplay)
                for j in range(0, len(headers)):
                    item.setText(j, str(i[headers[j]]))

    def populateTrades(self):
        orders = Messages.getInstance().trades.getMessages()
        if(len(orders)!=0):
            headers = list(orders[0].keys())
            self.GUI.tradesDisplay.clear()
            self.GUI.tradesDisplay.setHeaderLabels(headers)
            for i in orders:
                item = QtWidgets.QTreeWidgetItem(self.GUI.tradesDisplay)
                for j in range(0, len(headers)):
                    item.setText(j, str(i[headers[j]]))

    def populatePositions(self):
        positions = Messages.getInstance().positions.getMessages()
        if (len(positions) != 0):
            headers = list(positions[0].keys())
            self.GUI.positionsDisplay.clear()
            self.GUI.positionsDisplay.setHeaderLabels(headers)
            for i in positions:
                item = QtWidgets.QTreeWidgetItem(self.GUI.positionsDisplay)
                for j in range(0, len(headers)):
                    item.setText(j, str(i[headers[j]]))

    def populateStrategies(self):
        self.GUI.strategyBox.clear()
        self.GUI.strategyBox.setHeaderLabels(["Strategy"])
        keys = strategies.keys()
        LOGGER.info(keys)
        for i in range (0,len(keys)):
            item = QtWidgets.QTreeWidgetItem(self.GUI.strategyBox)
            item.setText(0,list(keys)[i])

    def populateRunningStrategies(self):
        root = self.GUI.strategyBox.invisibleRootItem()
        child_count = root.childCount()
        LOGGER.info("populateRunningStrategies")
        none_checked=True
        for i in range(child_count):
            item = root.child(i)
            checked = item.isSelected()
            strategy = item.text(0)
            strategy_to_execute = strategies[strategy]
            if checked:
                none_checked = False
                LOGGER.info(strategy_to_execute.attributes)
                self.GUI.runningStrategyBox.setHeaderLabels(strategy_to_execute.attributes)
        if none_checked:
            LOGGER.info(list(strategies.values())[0].attributes)
            self.GUI.runningStrategyBox.setHeaderLabels(list(strategies.values())[0].attributes)

    def startButtonClicked(self):
        LOGGER.info("start button clicked")
        root = self.GUI.strategyBox.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            checked = item.isSelected()
            strategy = item.text(0)
            strategy_to_execute = strategies[strategy]
            LOGGER.info(strategy_to_execute)
            if checked:
                Dialog = QtWidgets.QDialog()
                ui = StrategyInputBox()
                strategy_to_execute = strategy_to_execute()
                ui.setupUi(Dialog,strategy_to_execute)
                inputs = strategy_to_execute.define_inputs()
                for input, value in inputs.items():
                    if type(value) == list:
                        ui.addAttrList(input,value)
                    else:
                        ui.addAttr(input, value)
                Dialog.exec()
                return
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Oh no! Nothing is clicked')
        error_dialog.exec()

    def createButtonClicked(self):
        LOGGER.info("CREATE CLICKED")

    def editButtonClicked(self):
        LOGGER.info("EDIT BUTTON CLICKED")

    def stopButtonClicked(self):
        root = self.GUI.runningStrategyBox.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            checked = item.isSelected()
            portfolio_id = item.text(0)
            StrategyManager.get_instance().stop_strategy(portfolio_id=portfolio_id)

        LOGGER.info("STOP BUTTON CLICKED")

    def pauseButtonClicked(self):
        LOGGER.info("PAUSE BUTTON CLICKED")

    def stopAllButtonClicked(self):
        LOGGER.info("STOP ALL BUTTON CLICKED")

    def refreshRunningStrategies(self):
        self.populateRunningStrategies()

    def refreshOrders(self):
        self.orders = Messages.getInstance().orders.reset(BrokerManager.get_instance().get_data_broker().get_orders())
        self.populateOrders()
        LOGGER.info("refresh orders is called")

    def refreshTrades(self):
        self.trades = Messages.getInstance().trades.reset(BrokerManager.get_instance().get_data_broker().get_trades())
        self.populateTrades()
        LOGGER.info("refresh trades is called")

    def refreshPositions(self):
        self.positions = Messages.getInstance().trades.reset(BrokerManager.get_instance().get_data_broker().get_positions())
        self.populatePositions()
        LOGGER.info("refresh positions is called")

    def connect_components(self):
        self.GUI.startButton.clicked.connect(self.startButtonClicked)
        self.GUI.createButton.clicked.connect(self.createButtonClicked)
        self.GUI.editButton.clicked.connect(self.editButtonClicked)
        self.GUI.stopButton.clicked.connect(self.stopButtonClicked)
        self.GUI.stopAllButton.clicked.connect(self.stopAllButtonClicked)
        self.GUI.pauseButton.clicked.connect(self.pauseButtonClicked)
        self.GUI.strategyBox.clicked.connect(self.refreshRunningStrategies)
        self.GUI.ordersDisplay.clicked.connect(self.refreshOrders)
        self.GUI.tradesDisplay.clicked.connect(self.refreshTrades)
        self.GUI.positionsDisplay.clicked.connect(self.refreshPositions)

    def executeInitialFunctions(self,GUI=None):
        self.GUI=GUI
        self.populateTrades()
        self.populatePositions()
        self.populateUserMessages()
        self.populateBrokerMessages()
        self.populateOrders()
        self.populateStrategies()
        self.populateRunningStrategies()
        self.connect_components()

    __instance = None

    @staticmethod
    def get_instance():
        if GUIFunctions.__instance == None:
            GUIFunctions()
        return GUIFunctions.__instance

    def __init__(self):
        if GUIFunctions.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            GUIFunctions.__instance = self


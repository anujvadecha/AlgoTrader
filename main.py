import threading
import time
from Managers.BrokerManager import BrokerManager
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Managers.OrderManager import OrderManager
from Strategies.DemoStrategy import DemoStrategy
from UIElements.UIFirst import Ui_MainWindow
from PyQt5 import QtWidgets
from MessageClasses import Messages
import sys
from qt_material import apply_stylesheet
import logging
import logging.config
import os
from config import logging_config

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

class Main():

    def startMainWindow(self):
        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)
        MainWindow.show()
        sys.exit(app.exec_())

    def __init__(self):
        self.messages = Messages.getInstance()
        self.startMainWindow()


InstrumentManager.get_instance()
BrokerManager.get_instance()
MarketDataManager.get_instance()
OrderManager.get_instance()
main= Main()


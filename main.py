import threading
import time
from Managers.BrokerManager import BrokerManager
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Managers.StrategyManager import StrategyManager
from UIElements.UIFirst import Ui_MainWindow
from PyQt5 import QtWidgets
from MessageClasses import Messages
import sys
from qt_material import apply_stylesheet
import logging
import logging.config
import os
from config import logging_config
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AlgoApplication.settings")
import django

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

    def initialize_instances(self):
        BrokerManager.get_instance()
        InstrumentManager.get_instance()
        StrategyManager.get_instance()
        MarketDataManager.get_instance()

    def start_instance_thread(self):
        threading.Thread(target=self.initialize_instances).start()

    def __init__(self):
        # self.start_instance_thread()
        # con = sl.connect('algo_trader.db')
        self.messages = Messages.getInstance()
        django.setup()
        self.startMainWindow()

# InstrumentManager.get_instance()
MarketDataManager.get_instance()
# OrderManager.get_instance()
# BrokerManager.get_instance()
if __name__ == '__main__':
    main = Main()

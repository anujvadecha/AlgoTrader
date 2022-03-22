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

class Main():

    def startMainWindow(self):
        app = QtWidgets.QApplication(sys.argv)
        # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        apply_stylesheet(app, theme='light_blue.xml')
        MainWindow.show()
        sys.exit(app.exec_())

    def __init__(self):
        self.messages = Messages.getInstance()
        # self.messages.trades.addAll(self.broker.get_trades())
        # self.messages.positions.addAll(self.broker.get_positions())
        # self.messages.brokermessages.info("FIRST MESSAGE")
        # strat = DemoStrategy()
        # threading.Thread(target=strat.main).start()
        self.startMainWindow()



InstrumentManager.get_instance()
BrokerManager.get_instance()
time.sleep(2)
MarketDataManager.get_instance()
OrderManager.get_instance()
main= Main()


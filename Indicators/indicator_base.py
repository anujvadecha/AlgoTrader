from Managers import MarketDataManager
from MessageClasses import Messages


class Indicator:
    """
    base indicator class
    """
    def __init__(self):
        self.datamanager = MarketDataManager.get_instance()
        self.message = Messages.getInstance()
        self.preprocess()
        return

    def calculate(self):
        """
        placeholder for calculation logic
        """
        pass

    def preprocess(self):
        """
        placeholder for preprocess
        """
        pass

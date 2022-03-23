from Brokers.PaperTrading import PaperTradingBroker
from Brokers.ZerodhaBroker import ZerodhaBroker
from config import  brokers


class BrokerManager():

    alias_brokers = { }
    __datasource = None

    def get_broker(self, broker_alias):
        return self.alias_brokers[broker_alias]

    def get_data_broker(self):
        return self.__datasource

    def __load_brokers_from_config(self):
        for broker in brokers:
            if(broker["broker"]=="ZERODHA"):
                self.alias_brokers[broker["broker_alias"]] = ZerodhaBroker(broker["config"])
                self.alias_brokers[broker["broker_alias"]].connect()
            elif(broker["broker"]=="PAPER"):
                self.alias_brokers[broker["broker_alias"]] = PaperTradingBroker(broker["config"])
            if broker["dataSource"]:
                self.__datasource = self.alias_brokers[broker["broker_alias"]]
    __instance = None

    @staticmethod
    def get_instance():
        if BrokerManager.__instance == None:
            BrokerManager()
        return BrokerManager.__instance

    def __init__(self):
        if BrokerManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BrokerManager.__instance = self
        self.__load_brokers_from_config()
        self.__datasource.load_instruments()


if __name__=="__main__":
    BrokerManager.get_instance()

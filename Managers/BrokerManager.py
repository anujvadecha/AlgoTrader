from Brokers.ZerodhaBroker import ZerodhaBroker
from MessageClasses import Messages
from config import brokers


class BrokerManager():
    alias_brokers = {}
    __datasource = None

    def get_broker(self, broker_alias):
        return self.alias_brokers[broker_alias]

    def get_data_broker(self):
        return self.__datasource

    def __load_brokers_from_config(self):
        for broker in brokers:
            try:
                if broker["broker"] == "ZERODHA":
                    broker_to_connect = ZerodhaBroker(broker["config"])
                    broker_to_connect.connect()
                    self.alias_brokers[broker["broker_alias"]] = broker_to_connect
                if broker["dataSource"]:
                    self.__datasource = self.alias_brokers[broker["broker_alias"]]
            except Exception as e:
                Messages.getInstance().usermessages.info(
                    f"Could not connect {broker['broker_alias']} due to exception {e}")

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


if __name__ == "__main__":
    BrokerManager.get_instance()

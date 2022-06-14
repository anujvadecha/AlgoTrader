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
        from AlgoApp.models import Brokers
        for broker in brokers:
            try:
                is_existing = Brokers.objects.filter(broker_alias=broker["broker_alias"]).exists()
                print(is_existing)
                if not is_existing:
                    Brokers.objects.create(broker=broker["broker"],
                                           broker_alias=broker["broker_alias"],
                                           api_key=broker["config"]["apikey"],
                                           api_secret=broker["config"]["apisecret"],
                                           user_id=broker["config"]["userid"],
                                           password=broker["config"]["password"],
                                           pin=broker["config"]["pin"],
                                           totp_access_key=broker["config"]["totp_access_key"],
                                           live=broker["config"]["live"],
                                           datasource=broker["dataSource"])
            except Exception as e:
                Messages.getInstance().usermessages.info(
                    f"Could not connect {broker['broker_alias']} due to exception {e}")
        brokers_v1 = Brokers.objects.all()
        for broker in brokers_v1:
            try:
                if broker.broker == "ZERODHA":
                    broker_to_connect = ZerodhaBroker(broker)
                    broker_to_connect.connect()
                    self.alias_brokers[broker.broker_alias] = broker_to_connect
                if broker.datasource:
                    self.__datasource = self.alias_brokers[broker.broker_alias]
            except Exception as e:
                Messages.getInstance().usermessages.info(
                    f"Could not connect {broker.broker_alias} due to exception {e}")
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

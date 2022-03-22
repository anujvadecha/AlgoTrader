from kiteconnect import KiteConnect
import time
from selenium import webdriver
from urllib import parse
from kiteconnect import KiteTicker
import logging
import csv
from Models.Models import Instrument


class PaperTradingBroker():

    instrumentFactory = []
    orderFactory = []

    def place_market_order(self, instrument, side, quantity, type):
        order = self.kite.place_order(tradingsymbol=instrument.tradingsymbol,
                                      exchange=instrument.exchange,
                                      transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                      quantity=quantity,
                                      order_type=self.kite.ORDER_TYPE_MARKET,
                                      product=type,
                                      variety="regular")
        order = self.kite.order_history(order["data"]["order_id"])
        self.orderFactory.append(order)

    def place_limit_order(self, instrument, side, quantity, price):
        order = self.kite.place_order(
            tradingsymbol=instrument.tradingsymbol,
            exchange=instrument.exchange,
            transaction_type=self.kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            product=type,
            variety="regular",
            price=price
        )

    def subscribe(self, symbol):
        instrument = int(self.findInstrument(symbol).instrument_token)
        instrument = [instrument]
        print(instrument)
        self.tickerHandler.subscribe(instrument)
        self.tickerHandler.set_mode(self.tickerHandler.MODE_FULL, instrument)
        # self.kws.set_mode(self.kws.MODE_FULL,instrument.instrument_token)

    def on_connect(self, ws, response):
        print(" ON CONNECT ")
        self.tickerHandler = ws
        pass

    def on_close(broker, ws, code, reason):
        # On connection close stop the event loop.
        # Reconnection will not happen after executing `ws.stop()`
        ws.stop()

    def __readInstrumentsfromCsv(self):
        with open("../BrokerCache/instruments.csv", "r") as f:
            reader = csv.DictReader(f)
            a = list(reader)
        if (len(a) <= 0):
            raise Exception("NOT ENOUGH INSTRUMENTS")
        return a;

    def findInstrument(self, symbol):
        for instrument in self.instrumentFactory:
            if instrument.tradingsymbol == symbol:
                return instrument
        raise Exception("INSTRUMENT NOT FOUND ")

    # def subscribeMarketData(self,instrument):

    def connect(self):
        try:
            self.kite = KiteConnect(api_key=self.apikey)
            self.kite.set_access_token(self.__read_accesstocken())
            self.kite.trades()
        except:
            self.kite = KiteConnect(api_key=self.apikey)
            driver = webdriver.Chrome("chromedriver")
            driver.get(self.kite.login_url())
            time.sleep(2)
            element = driver.find_elements_by_tag_name("input")
            element[0].send_keys(self.userid)
            element[1].send_keys(self.password)
            element = driver.find_elements_by_tag_name("button")
            element[0].click()
            time.sleep(2)
            element = driver.find_elements_by_tag_name("input")
            element[0].send_keys(self.pin)
            element = driver.find_elements_by_tag_name("button")
            element[0].click()
            time.sleep(2)
            url = driver.current_url
            query_def = parse.parse_qs(parse.urlparse(url).query)
            driver.close()
            data = self.kite.generate_session(query_def["request_token"][0], api_secret=self.apisecret)
            self.kite.set_access_token(data["access_token"])
            self.__write_accesstocken(data["access_token"])
            self.kws = KiteTicker(self.apikey, data["access_token"])
            self.kws.on_ticks = self.__tickerOnTicks
            self.kws.on_connect = self.on_connect
            self.kws.on_close = self.on_close
            self.kws.on_order_update = self.__tickerOnOrderUpdate
            self.kws.on_noreconnect = self.__tickerOnNoReconnect
            self.kws.connect()
        self.__instrument_store()
        self.kws = KiteTicker(self.apikey, self.__read_accesstocken())
        self.kws.on_ticks = self.__tickerOnTicks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.connect(threaded=True)
        # marketdatathread = threading.Thread(target=self.kws.connect)
        # marketdatathread.start()
        # self.kws.connect()

    def initializeconfig(self, config):
        self.apikey = config["apikey"]
        self.apisecret = config["apisecret"]
        self.userid = config["userid"]
        self.password = config["password"]
        self.pin = config["pin"]

    def getOrders(self):
        return self.kite.orders()

    def getTrades(self):
        return self.kite.trades()

    def getPositions(self):
        # pprint(self.kite.positions())
        return self.kite.positions()["net"]

    def getHoldings(self):
        return self.kite.holdings()

    def getHistoricalData(self, instrument, fromdate, to, interval):
        return self.kite.historical_data(int(self.findInstrument(instrument).instrument_token), fromdate, to, interval,
                                         False, False)

    def __read_accesstocken(self):
        file = open("../BrokerCache/accesstoken.txt", "r")
        line = file.read()
        print(line)
        return line

    def __write_accesstocken(self, accesstocken):
        f = open("../BrokerCache/accesstoken.txt", "w")
        f.write(accesstocken)
        f.close()

    def __tickerOnOrderUpdate(self, ws, data):
        print(data)
        pass

    def __tickerOnError(self, ws, code, reason):
        print(str(code) + str(reason))
        pass

    def __tickerOnNoReconnect(self):
        print("CANT RECONNECT")
        pass

    def __writeDictToCSV(filename, dictofinst):
        with open(filename, 'w', encoding='utf8', newline='') as output_file:
            fc = csv.DictWriter(
                output_file,
                fieldnames=dictofinst[0].keys(),
            )
            fc.writeheader()
            fc.writerows(dictofinst)

    def __tickerOnTicks(self, ws, ticks):
        logging.debug("Ticks: {}".format(ticks))
        print("Ticks: {}".format(ticks))

    def __instrument_store(self):
        print("instrument store called")
        try:
            instruments = self.__readInstrumentsfromCsv()
        except:
            print("ordering from zerodha")
            instruments = self.kite.instruments(exchange=self.kite.EXCHANGE_NSE)
            print("instruments" + str(len(instruments)))
            self.__writeDictToCSV("./BrokerCache/instruments.csv", instruments)
            print("written to csv")
        for instrument in instruments:
            self.instrumentFactory.append(Instrument(*instrument.values()))
        return instruments

    def __init__(self,broker):
        pass
        # self.initializeconfig(broker)
        # if PaperTradingBroker.__instance != None:
        #     raise Exception("This class is a singleton!")
        # else:
        #     PaperTradingBroker.__instance = self

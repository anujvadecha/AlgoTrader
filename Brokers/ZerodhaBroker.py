import os
import pyotp
from kiteconnect import KiteConnect
import time
from selenium import webdriver
from urllib import parse
from kiteconnect import KiteTicker
import logging
import csv
from Managers.InstrumentManager import InstrumentManager
from Managers.MarketDataManager import MarketDataManager
from Core.Broker import Broker
from Models.Models import Instrument, Tick
from MessageClasses import Messages

class ZerodhaBroker(Broker):

    subscribe_cache={}

    def placeMarketOrder(self, instrument, side, quantity, type):
        order = self.kite.place_order(tradingsymbol=instrument.tradingsymbol,
                                      exchange=instrument.exchange,
                                      transaction_type=self.kite.TRANSACTION_TYPE_SELL,
                                      quantity=quantity,
                                      order_type=self.kite.ORDER_TYPE_MARKET,
                                      product=type,
                                      variety="regular")
        order = self.kite.order_history(order["data"]["order_id"])

    def placeLimitOrder(self, instrument, side, quantity, price):
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

    def subscribe(self, instrument:Instrument):
        self.subscribe_cache[instrument.instrument_token] = instrument.tradingsymbol
        self.tickerHandler.subscribe([int(instrument.instrument_token)])

    def on_connect(self, ws, response):
        self.tickerHandler = ws
        pass

    def on_close(broker, ws, code, reason):
        print(f"connection closed by broker class {reason}")
        ws.stop()

    def __readInstrumentsfromCsv(self):
        with open(os.getcwd()+"/BrokerCache/instruments.csv", "r") as f:
            reader = csv.DictReader(f)
            a = list(reader)
        if (len(a) <= 0):
            raise Exception("NOT ENOUGH INSTRUMENTS")
        return a

    def connect(self):
        from selenium import webdriver
        import chromedriver_autoinstaller
        chromedriver_autoinstaller.install()
        try:
            self.kite = KiteConnect(api_key=self.apikey)
            self.kite.set_access_token(self.__read_accesstocken())
            self.kite.trades()
        except:
            self.kite = KiteConnect(api_key=self.apikey)
            driver = webdriver.Chrome()
            driver.get(self.kite.login_url())
            time.sleep(2)
            element = driver.find_elements_by_tag_name("input")
            element[0].send_keys(self.userid)
            element[1].send_keys(self.password)
            element = driver.find_elements_by_tag_name("button")
            element[0].click()
            time.sleep(2)
            element = driver.find_elements_by_tag_name("input")
            totp = pyotp.TOTP(self.totp_access_key)
            element[0].send_keys(totp.now())
            element = driver.find_elements_by_tag_name("button")
            element[0].click()
            time.sleep(2)
            url = driver.current_url
            query_def = parse.parse_qs(parse.urlparse(url).query)
            driver.close()
            data = self.kite.generate_session(query_def["request_token"][0], api_secret=self.apisecret)
            self.kite.set_access_token(data["access_token"])
            self.__write_accesstocken(data["access_token"])
        self.kws = KiteTicker(self.apikey, self.__read_accesstocken())
        self.kws.on_ticks = self.__tickerOnTicks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_order_update = self.__tickerOnOrderUpdate
        self.kws.on_noreconnect = self.__tickerOnNoReconnect
        self.kws.connect(threaded=True)
        messages = Messages.getInstance()
        messages.trades.addAll(self.get_trades())
        messages.positions.addAll(self.get_positions())
        messages.orders.addAll(self.get_orders())

    def get_ticker_connection(self):
        return self.kws

    def load_instruments(self):
        self.__instrument_store()

    def initialize(self, config):
        self.apikey = config["apikey"]
        self.apisecret = config["apisecret"]
        self.userid = config["userid"]
        self.password = config["password"]
        # self.pin = config["pin"]
        self.totp_access_key = config['totp_access_key']

    def get_orders(self):
        print("get orders called")
        return self.kite.orders()

    def get_trades(self):
        return self.kite.trades()

    def get_positions(self):
        return self.kite.positions()["net"]

    def get_holdings(self):
        return self.kite.holdings()

    def get_historical_data(self, instrument: Instrument, from_date, to_date, interval):
        return self.kite.historical_data(int(instrument.instrument_token), from_date, to_date, interval,
                                         False, False)

    def __read_accesstocken(self):
        file = open(os.getcwd()+"/BrokerCache/accesstoken.txt", "r")
        line = file.read()
        return line

    def __write_accesstocken(self, accesstocken):
        f = open(os.getcwd()+"/BrokerCache/accesstoken.txt", "w")
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

    def __writeDictToCSV(self,filename, dictofinst):
        with open(filename, 'w', encoding='utf8', newline='') as output_file:
            fc = csv.DictWriter(
                output_file,
                fieldnames=dictofinst[0].keys(),
            )
            fc.writeheader()
            fc.writerows(dictofinst)

    def __tickerOnTicks(self, ws, ticks):
        for tick in ticks:
            tick_to_push = Tick(
                symbol=self.subscribe_cache[tick["instrument_token"]],
                volume=tick["volume"],
                ltp=tick["last_price"],
                buy_quantity=tick["buy_quantity"],
                sell_quantity=tick["sell_quantity"],
                average_price=tick["average_price"],
                bid=None,
                ask=None,
                bid_qty=None,
                ask_qty=None,
                last_qty=None,
                ltt=None,
                open=tick["ohlc"]["open"],
                high=tick["ohlc"]["high"],
                low=tick["ohlc"]["low"],
                close=tick["ohlc"]["close"]
            )
            self.push_L1_data(tick_to_push)
            logging.debug("Tick: {}".format(tick))

    def __instrument_store(self):
        try:
            instruments = self.__readInstrumentsfromCsv()
            raise Exception("fail")
        except:
            instruments = self.kite.instruments(exchange=self.kite.EXCHANGE_NSE)
            nfo_instruments = self.kite.instruments(exchange=self.kite.EXCHANGE_NFO)
            instruments.extend(nfo_instruments)
            # instruments.append(nfo_instruments)
            self.__writeDictToCSV(os.getcwd()+"/BrokerCache/instruments.csv", instruments)
        for instrument in instruments:
            self.push_instrument(Instrument(*instrument.values()))
        return instruments

    def get_connection_object(self):
        return self.kite

    def __init__(self,config):
        self.initialize(config)

if __name__=="main":
    ZerodhaBroker(None)

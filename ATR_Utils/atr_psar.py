import datetime
import json
import logging

import pandas as pd
from ATR_Utils.execution_logic import ExecutionLogic
from ATR_Utils.indicator_manager import IndicatorManager
from ATR_Utils.position_manager import PositionManager
import ATR_Utils.indicators as indicators
from Managers.InstrumentManager import InstrumentManager
import Core.Strategy

LOGGER = logging.getLogger(__name__)


# classes
class ExecutionData:
    def __init__(self):
        self.running_pos = None
        self.running_pos_type = None
        self.prev_close = 0.00
        self.trading = True
        self.can_trade = {"param1": {'bullish': True, 'bearish': True},
                          "param2": {'bullish': True, 'bearish': True},
                          "param3": {'bullish': True, 'bearish': True},
                          "param4": {'bullish': True, 'bearish': True},
                          "param1 alt": {'bullish': True, 'bearish': True},
                          "param2 alt": {'bullish': True, 'bearish': True},
                          "param3 alt": {'bullish': True, 'bearish': True},
                          "param4 alt": {'bullish': True, 'bearish': True}}
        self.cdl_size = 0.00
        self.trade_temp = {"trade param": None,
                           "trade action": None,
                           "entry_time": None,
                           "entry_price": None,
                           "entry_atr": None,
                           "stoploss": None,
                           "target": None,
                           "exit_time": None,
                           "exit_price": None,
                           "exit_type": None,
                           "candle": None,
                           "stoch": None,
                           "pivot": None}

        self.trade = self.trade_temp.copy()
        self.trade_entry = False
        self.trade_exit = False
        self.in_trade = False
        self.last_trade = self.trade_temp.copy()
        self.trade_entry_copy = False


data_obj = None
con_obj = None
msg_obj = None  # type: Core.Strategy.Strategy
sys_inputs = None
orders_type = ""
order_instrument = ""
option_expiry = ""
order_quantity = ""
option_quantity = ""
instrument_list = []
symbol = ""
option_entry_instrument = None
expiry = None  # type: datetime.datetime
spot_data = {}
sub_token = []

pm = None  # type: PositionManager
IM = None  # type: IndicatorManager

chart = None  # type: indicators.CandleSticksChart
psar = None  # type: indicators.ParabolicSAR
st = None  # type: indicators.Supertrend
atr = None  # type: indicators.AverageTrueRange
stoch = None  # type: indicators.Stochastic
pp = None  # type: indicators.PivotPoints
trade_dir = None  # type: pd.DataFrame

exc_log = None  # type: ExecutionLogic
exc_data = ExecutionData()

file_name = ""


# helper functions
def fill_orders2(ticks):
    global pm, spot_data, msg_obj, LOGGER
    tick_data = None
    for tick in ticks:
        if tick["instrument_token"] == spot_data["instrument_token"]:
            tick_data = tick
    if exc_data.trade_entry:
        exc_data.trade_entry = False
        exc_data.trade["entry_time"] = tick_data["exchange_timestamp"]
        exc_data.trade["entry_price"] = tick_data["last_price"]
        if "alt" in exc_data.trade["trade param"]:
            if exc_data.trade["trade action"] == "buy":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.running_pos_type = "LONG"
                place_entry_order("BUY")
            elif exc_data.trade["trade action"] == "sell":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.running_pos_type = "SHORT"
                place_entry_order("SELL")
        else:
            if exc_data.trade["trade action"] == "buy":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"]), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"]), 2)
                exc_data.running_pos_type = "LONG"
                place_entry_order("BUY")
            elif exc_data.trade["trade action"] == "sell":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"]), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"]), 2)
                exc_data.running_pos_type = "SHORT"
                place_entry_order("SELL")
        msg_obj.add_info_user_message(
            f"trade type {exc_data.running_pos_type}, @  {exc_data.trade['entry_price']}, parameter: {exc_data.trade['trade param']}, time: {tick_data['exchange_timestamp']}")
        LOGGER.info(
            f"trade type {exc_data.running_pos_type}, @  {exc_data.trade['entry_price']}, parameter: {exc_data.trade['trade param']}, time: {tick_data['exchange_timestamp']}")


def system_setup(inputs):  # add proper use of inputs
    """
    populates the global variables
    """
    global instrument_list, spot_data, pm, IM, chart, psar, st, atr, stoch, pp, \
        data_obj, exc_log, trade_dir, sub_token, msg_obj, orders_type, order_instrument, option_expiry, order_quantity,\
        option_quantity, symbol, exc_data, file_name, option_entry_instrument

    orders_type = inputs["orders_type"]
    order_instrument = inputs["order_instrument"]
    option_expiry = inputs["option_expiry"]
    order_quantity = int(inputs["order_quantity"])
    option_quantity = int(inputs["option_quantity"])

    instrument_list = data_obj.instruments(exchange=data_obj.EXCHANGE_NFO)

    spot_symbol = inputs['symbol']
    if "BANKNIFTY" in spot_symbol:
        symbol = "BANKNIFTY"
    else:
        symbol = "NIFTY"

    for instru in instrument_list:
        if instru['tradingsymbol'] == spot_symbol:
            spot_data = instru
            break

    # LOGGER.debug(f'instrument : {spot_data}')
    pm = PositionManager(data_obj)
    print(spot_data)

    # indicator and chart setup
    IM = IndicatorManager(spot_data, data_obj)
    indicators_used = []
    timeframe = int(inputs['timeframe'])

    chart = indicators.CandleSticksChart(timeframe=timeframe)
    psar = indicators.ParabolicSAR(timeframe=timeframe)
    st = indicators.Supertrend(timeframe=timeframe)
    atr = indicators.AverageTrueRange(timeframe=timeframe)
    stoch = indicators.Stochastic(k_length=5, k_smooth=3, d_smooth=3, timeframe=timeframe)
    pp = indicators.PivotPoints(timeframe=timeframe)

    indicators_used.append(chart)
    indicators_used.append(psar)
    indicators_used.append(st)
    indicators_used.append(atr)
    indicators_used.append(stoch)
    indicators_used.append(pp)
    IM.add_indicators(indicators_used)

    msg_obj.add_info_user_message(f'psar : {psar.PSAR} trend({psar.trend})')
    msg_obj.add_info_user_message(f'atr : {atr.ATR}')
    msg_obj.add_info_user_message(f'supertrend : {st.supertrend} trend({st.trend})')
    msg_obj.add_info_user_message(f'stoch : k({stoch.k_value}) d({stoch.d_value})')
    msg_obj.add_info_user_message(f'pivots : {pp.pivots}')

    exc_log = ExecutionLogic(timeframe=timeframe)

    disc_loc = ""
    if symbol == "NIFTY":
        disc_loc = "resources/ATR_NF_disc.csv"
    else:
        disc_loc = "resources/ATR_BNF_disc.csv"

    trade_df = pd.read_csv(disc_loc)
    trade_dir = trade_df.to_dict('records')
    print(trade_dir)

    exc_log.execution_logic = exc_seq
    sub_token = spot_data["instrument_token"]

    if symbol == "NIFTY":
        file_name = "resources/atr_nf_trade.txt"
    else:
        file_name = "resources/atr_bnf_trade.txt"

    with open(file_name, 'r') as file:
        data = file.read()

    prev_trade = json.loads(data)

    if prev_trade['overnight']:
        print('loading data')
        exc_data.in_trade = True
        exc_data.trade["trade action"] = prev_trade["trade action"]
        exc_data.trade["entry_price"] = prev_trade["entry_price"]
        exc_data.trade["stoploss"] = prev_trade["stoploss"]
        exc_data.trade["target"] = prev_trade["target"]
        option_entry_instrument = prev_trade["option_entry_instrument"]
        order_instrument = prev_trade["order_instrument"]
    else:
        print("no overnight trade")


def place_entry_order(side, identifier=None):
    global option_entry_instrument
    entry_price = chart.running_cdl["close"]
    option_entry_instrument = None
    if orders_type != "OPTIONS_ONLY":
        msg_obj.add_info_user_message(
            f"Placing entry order for {order_instrument} {side} {order_quantity} {identifier}")
    # Futures order
    # TODO: enable
    # place_market_order(instrument=order_instrument, side=side,
    #                            quantity=order_quantity, type="NRML")
    # Options order
    if orders_type != "FUTURES_ONLY":
        if entry_price % 100 < 50:
            targeted_strike_price = entry_price - entry_price % 100
        else:
            targeted_strike_price = entry_price + (100 - entry_price % 100)
        if side == "BUY":
            option_intruments = InstrumentManager.get_instance().get_call_options_for_instrument(symbol,
                                                                                                 strike=targeted_strike_price)
        else:
            option_intruments = InstrumentManager.get_instance().get_put_options_for_instrument(
                symbol,
                strike=targeted_strike_price)
        for optioninstr in option_intruments:
            if str(optioninstr.expiry) == option_expiry:
                option_entry_instrument = optioninstr
                break
        if option_entry_instrument:
            msg_obj.add_info_user_message(
                f"Placing entry order for {option_entry_instrument} BUY {option_quantity} {identifier}")
            # TODO: enable
            # self.place_market_order(instrument=self.option_entry_instrument, side="BUY",
            #                                quantity=self.option_quantity, type="NRML")
        else:
            msg_obj.add_info_user_message(f"Option entry not found for {targeted_strike_price} {symbol}")


def place_exit_order(side, identifier=None):
    global option_entry_instrument
    if orders_type != "OPTIONS_ONLY":
        msg_obj.add_info_user_message(
            f"Placing exit order for {order_instrument} {side} {order_quantity} {identifier}")
        # self.place_market_order(instrument=self.order_instrument,
        #                                side=side, quantity=self.order_quantity,
        #                                type="NRML")
    if orders_type != "FUTURES_ONLY" and option_entry_instrument:
        msg_obj.add_info_user_message(
            f"Placing exit order for {option_entry_instrument} SELL {option_quantity} {identifier}")
        # self.place_market_order(instrument=self.option_entry_instrument,
        #                                side="SELL", quantity=self.option_quantity,
        #                                type="NRML")


def entries():
    global chart, psar, atr, stoch, pp, trade_dir, exc_data, msg_obj

    msg_obj.add_info_user_message(f'candle :{chart.closed_cdl}')
    LOGGER.info(f'candle :{chart.closed_cdl}')
    t_stp = chart.closed_time
    if exc_data.in_trade:
        exc_data.trade_entry_copy = False
        return

    if t_stp is None:
        return

    tick_time = (chart.closed_time.hour * 100) + chart.closed_time.minute
    if tick_time >= 1515:
        return
    exc_data.trade = exc_data.trade_temp.copy()

    closed = chart.closed_cdl
    candle_size = abs(closed["open"] - closed["close"])

    exc_data.trade_entry_copy = False

    param = ""
    msg_obj.add_info_user_message(f'psar {psar.trend} st {st.trend}')
    # parameter determinations
    if psar.trend > 0 and st.trend > 0:
        # PSAR buy ST buy
        if atr.ATR < candle_size:
            param = "param1"
    elif psar.trend < 0 and st.trend > 0:
        # PSAR sell ST buy
        if atr.ATR < candle_size:
            param = "param2"
    elif psar.trend > 0 and st.trend < 0:
        # PSAR buy ST sell
        if atr.ATR < candle_size:
            param = "param3"
    elif psar.trend < 0 and st.trend < 0:
        # PSAR sell ST sell
        if atr.ATR < candle_size:
            param = "param4"
    # LOGGER.debug('found param')
    if param == "":
        return
    # alternate condition check
    alt = ""
    if candle_size > (atr.ATR * 2.00):
        alt = " alt"

    # candle type
    candle_type = "bullish"
    if closed["open"] > closed["close"]:
        candle_type = "bearish"

    # stoch
    stoch_sig = stoch.signal

    # pivot condition
    pivot_range = pp.check_pivot(chart.running_cdl.copy())
    pivot_range_copy = pivot_range
    # trade parameter filtering
    final_param = param + alt

    if not exc_data.can_trade[final_param][candle_type]:
        return

    trade_type = None
    for dec in trade_dir:
        if dec['param'] == final_param:
            if dec['candle'] == candle_type:
                if dec['stoch'] == stoch_sig:
                    if dec['pivot'] == pivot_range:
                        trade_type = (dec['decision'])
    # LOGGER.debug('found trade type')
    if trade_type == "no_trade":
        return

    exc_data.trade["trade param"] = final_param
    exc_data.trade["trade action"] = trade_type
    exc_data.trade["entry_atr"] = atr.ATR
    exc_data.trade["candle"] = candle_type
    exc_data.trade["pivot"] = pivot_range_copy
    exc_data.trade["stoch"] = stoch.signal
    exc_data.trade_entry = True
    exc_data.in_trade = True

    exc_data.can_trade[final_param][candle_type] = False
    # LOGGER.debug('exit entries')


def exits():
    global msg_obj
    if exc_data.in_trade:
        if exc_data.trade["trade action"] == "buy":
            if chart.running_cdl["close"] >= exc_data.trade["target"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["target"]
                exc_data.trade["exit_type"] = "target"
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                msg_obj.add_info_user_message(f"target reached @ {chart.running_cdl['close']}")
                place_exit_order("SELL")
        else:
            if chart.running_cdl["close"] <= exc_data.trade["target"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["target"]
                exc_data.trade["exit_type"] = "target"
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                msg_obj.add_info_user_message(f"target reached @ {chart.running_cdl['close']}")
                place_exit_order("BUY")
    return


def stops():
    global msg_obj
    if exc_data.in_trade:
        if exc_data.trade["trade action"] == "buy":
            if chart.running_cdl["close"] <= exc_data.trade["stoploss"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["stoploss"]
                exc_data.trade["exit_type"] = "stoploss"
                msg_obj.add_info_user_message(
                    f"stoploss @ {chart.running_cdl['close']} @ {chart.running_cdl['timestamp']}")
                place_exit_order("SELL")
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                exc_data.trade_exit = True
        else:
            if chart.running_cdl["close"] >= exc_data.trade["stoploss"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["stoploss"]
                exc_data.trade["exit_type"] = "stoploss"
                msg_obj.add_info_user_message(
                    f"stoploss @ {chart.running_cdl['close']} @ {chart.running_cdl['timestamp']}")
                place_exit_order("BUY")
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                exc_data.trade_exit = True
    return


def eod_exit():
    now = datetime.datetime.now()
    if now.hour == 15 and now.minute >= 30 and now.second >= 15:
        saved_dict = {}
        if exc_data.in_trade:
            saved_dict["overnight"] = True
            saved_dict["trade action"] = exc_data.trade["trade action"]
            saved_dict["entry_price"] = exc_data.trade["entry_price"]
            saved_dict["stoploss"] = exc_data.trade["stoploss"]
            saved_dict["target"] = exc_data.trade["target"]
            saved_dict["option_entry_instrument"] = option_entry_instrument.tradingsymbol
            saved_dict["order_instrument"] = order_instrument

        else:
            saved_dict["overnight"] = False
            saved_dict["trade action"] = None
            saved_dict["entry_price"] = None
            saved_dict["stoploss"] = None
            saved_dict["target"] = None
            saved_dict["option_entry_instrument"] = None
            saved_dict["order_instrument"] = None

        with open(file_name, 'w') as file:
            file.write(json.dumps(saved_dict))

        # kws1.close()
    return


def exc_seq():
    exc_data.trade_exit = False
    eod_exit()
    # LOGGER.debug('calculate exits')
    exits()
    # LOGGER.debug('calculate stops')
    stops()
    if chart.new_candle:
        # LOGGER.debug('calculate entries')
        entries()


# starting execution -----------------
# Initialise
# kws1 = KiteTicker(key_secret[0], data["access_token"])


def on_ticks(ws, ticks):
    try:
        # Callback to receive ticks.
        # LOGGER.debug(f'ticks_rec : {ticks}')
        # LOGGER.debug('enter im')
        IM.new_ticks(ticks)
        # LOGGER.debug('enter exc')
        exc_log.execute()
        # LOGGER.debug('enter fo')
        fill_orders2(ticks)
    except Exception as e:
        LOGGER.info(f"exception : {e}")


def on_connect(ws, response):
    global sub_token
    print("connection successfully")
    # Callback on successful connect.
    if ws.subscribe([sub_token]):
        print("connected")
    ws.set_mode(ws.MODE_FULL, [sub_token])


def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    LOGGER.info(f"connection closed {reason}")
    # ws.stop()


def on_order_update(ws, data):
    print(data)


# def on_message(ws,data,isbinary):
#     print(data)
kws1 = None


def ATR_trigger_start(connection_object, data_connection_object, ticker_connection_object, inputs, messaging,
                      strategy_obj):
    global data_obj, con_obj, msg_obj, sys_inputs, kws1
    data_obj = data_connection_object
    con_obj = connection_object
    sys_inputs = inputs
    msg_obj = strategy_obj
    system_setup(sys_inputs)
    msg_obj.add_info_user_message(f"ATR started with inputs {inputs}")
    kws1 = ticker_connection_object
    # ticker_connection_object.close()
    kws1.on_ticks = on_ticks
    kws1.on_connect = on_connect
    kws1.on_close = on_close
    kws1.on_order_update = on_order_update
    # kws1.on_message = on_message
    kws1.connect(threaded=True)
    #
    # backtest()


def ATR_trigger_stop():
    global msg_obj, kws1
    msg_obj.add_info_user_message("Stopping things")
    # TODO add square-off functions
    msg_obj.add_info_user_message("perform square-off")
    # kws1.stop()


def backtest():
    global data_obj, spot_data
    from_date = datetime.datetime.now() - datetime.timedelta(days=1)
    to_date = datetime.datetime.now() - datetime.timedelta(days=1)
    hist = data_obj.historical_data(spot_data["instrument_token"], from_date.strftime("%Y-%m-%d"),
                                    to_date.strftime("%Y-%m-%d"), 'minute')
    hist_df = pd.DataFrame(hist)
    hist_df["cum_vol"] = hist_df["volume"].cumsum()
    print(hist_df.head())
    print(hist_df.tail())
    # build price ticks
    ticks = []
    for index, row in hist_df.iterrows():
        temp = {"instrument_token": spot_data["instrument_token"], "timestamp": None, "last_price": None,
                "volume": None}
        time = row["date"]
        temp["timestamp"] = time
        temp["last_price"] = row["open"]
        temp["volume"] = row["cum_vol"] - 300
        if index == 0:
            temp["volume"] = 0
        temp = [temp]
        ticks.append(temp.copy())
        del temp
        temp = {"instrument_token": spot_data["instrument_token"], "timestamp": time + datetime.timedelta(seconds=12),
                "last_price": row["high"], "volume": row["cum_vol"] - 200}
        temp = [temp]
        ticks.append(temp.copy())
        del temp
        temp = {"instrument_token": spot_data["instrument_token"], "timestamp": time + datetime.timedelta(seconds=12),
                "last_price": row["low"], "volume": row["cum_vol"] - 100}
        temp = [temp]
        ticks.append(temp.copy())
        del temp
        temp = {"instrument_token": spot_data["instrument_token"], "timestamp": time + datetime.timedelta(seconds=12),
                "last_price": row["close"], "volume": row["cum_vol"]}
        temp = [temp]
        ticks.append(temp.copy())
        del temp
    ticks[-1][0]["timestamp"] = ticks[-1][0]["timestamp"] + datetime.timedelta(minutes=2)

    for tick in ticks:
        on_ticks(0, tick)

    eod_exit()

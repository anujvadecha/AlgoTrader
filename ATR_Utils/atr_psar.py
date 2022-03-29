import datetime
import pandas as pd
from ATR_Utils.execution_logic import ExecutionLogic
from ATR_Utils.indicator_manager import IndicatorManager
from ATR_Utils.position_manager import PositionManager
from ATR_Utils.positions import Position
import ATR_Utils.indicators as indicators


# classes
# position setup
class LongPosition(Position):
    def __init__(self, spot_price):
        global instrument_list
        strike = (spot_price // 50) * 50
        if spot_price - strike > 40:
            strike += 50
        strike_type = "CE"
        strike_data = None
        for i in range(len(instrument_list)):
            if instrument_list[i]['strike'] == strike:
                if instrument_list[i]['instrument_type'] == strike_type:
                    if instrument_list[i]['expiry'] == expiry.date():
                        strike_data = instrument_list[i]
                        break
        super().__init__(strike_data, Position.TYPE_LONG, 50)
        print("long position in", strike_data["tradingsymbol"])


class ShortPosition(Position):
    def __init__(self, spot_price):
        global instrument_list
        strike = (spot_price // 50) * 50
        if spot_price - strike > 10:
            strike += 50
        strike_type = "PE"
        strike_data = None
        for i in range(len(instrument_list)):
            if instrument_list[i]['strike'] == strike:
                if instrument_list[i]['instrument_type'] == strike_type:
                    if instrument_list[i]['expiry'] == expiry.date():
                        strike_data = instrument_list[i]
                        break
        super().__init__(strike_data, Position.TYPE_LONG, 50)
        print("long position in", strike_data["tradingsymbol"])


class ExecutionData:
    def __init__(self):
        self.running_pos = None
        self.running_pos_type = None
        self.prev_close = 0.00
        self.trading = True
        self.can_trade = {"param1": {'bullish': True,
                                     'bearish': True},
                          "param2": {'bullish': True,
                                     'bearish': True},
                          "param3": {'bullish': True,
                                     'bearish': True},
                          "param4": {'bullish': True,
                                     'bearish': True},
                          "param1 alt": {'bullish': True,
                                         'bearish': True},
                          "param2 alt": {'bullish': True,
                                         'bearish': True},
                          "param3 alt": {'bullish': True,
                                         'bearish': True},
                          "param4 alt": {'bullish': True,
                                         'bearish': True}}
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

        self.trade = {"trade param": None,
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
        self.trade_entry = False
        self.trade_exit = False
        self.in_trade = False
        self.last_trade = self.trade_temp.copy()
        self.trade_entry_copy = False

    def reset(self):
        self.can_trade = {"param1": {'bullish': True, 'bearish': True},
                          "param2": {'bullish': True, 'bearish': True},
                          "param3": {'bullish': True, 'bearish': True},
                          "param4": {'bullish': True, 'bearish': True},
                          "param1 alt": {'bullish': True, 'bearish': True},
                          "param2 alt": {'bullish': True, 'bearish': True},
                          "param3 alt": {'bullish': True, 'bearish': True},
                          "param4 alt": {'bullish': True, 'bearish': True}}


data_obj = None
con_obj = None
msg_obj = None
sys_inputs = None
instrument_list = []
expiry = None
spot_data = None
sub_token = None

pm = None
IM = None

chart = None
psar = None
st = None
atr = None
stoch = None
pp = None
trade_dir = None

exc_log = None
exc_data = ExecutionData()


# helper functions
def coming_expiry():  # missing expiry switching
    dt_now = datetime.datetime.now()
    if dt_now.weekday() > 3:
        delta = 10 - dt_now.weekday()
    else:
        delta = 3 - dt_now.weekday()
    return dt_now + datetime.timedelta(days=delta)


def fill_orders(tick):  # redo
    global pm
    if exc_data.trade_entry:
        exc_data.trade_entry = False
        exc_data.trade["entry_time"] = tick["timestamp"]
        exc_data.trade["entry_price"] = tick["last_price"]
        if "alt" in exc_data.trade["trade param"]:
            if exc_data.trade["trade action"] == "buy":
                exc_data.trade["stoploss"] = round(
                    tick["last_price"] - (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.trade["target"] = round(
                    tick["last_price"] + (exc_data.trade["entry_atr"] * 1.5), 2)
                new_pos = LongPosition(tick["last_price"])
                if exc_data.running_pos is not None:
                    pm.close_position(exc_data.running_pos)
                new_pos_id = pm.new_position(new_pos)
                pm.enter_position(new_pos_id)
                exc_data.running_pos = new_pos_id
                exc_data.running_pos_type = "LONG"
            elif exc_data.trade["trade action"] == "sell":
                exc_data.trade["stoploss"] = round(
                    tick["last_price"] + (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.trade["target"] = round(
                    tick["last_price"] - (exc_data.trade["entry_atr"] * 1.5), 2)
                new_pos = ShortPosition(tick["last_price"])
                if exc_data.running_pos is not None:
                    pm.close_position(exc_data.running_pos)
                new_pos_id = pm.new_position(new_pos)
                pm.enter_position(new_pos_id)
                exc_data.running_pos = new_pos_id
                exc_data.running_pos_type = "SHORT"
        else:
            if exc_data.trade["trade action"] == "buy":
                exc_data.trade["stoploss"] = round(
                    tick["last_price"] - (exc_data.trade["entry_atr"]), 2)
                exc_data.trade["target"] = round(
                    tick["last_price"] + (exc_data.trade["entry_atr"]), 2)
                new_pos = LongPosition(tick["last_price"])
                if exc_data.running_pos is not None:
                    pm.close_position(exc_data.running_pos)
                new_pos_id = pm.new_position(new_pos)
                pm.enter_position(new_pos_id)
                exc_data.running_pos = new_pos_id
                exc_data.running_pos_type = "LONG"
            elif exc_data.trade["trade action"] == "sell":
                exc_data.trade["stoploss"] = round(
                    tick["last_price"] + (exc_data.trade["entry_atr"]), 2)
                exc_data.trade["target"] = round(
                    tick["last_price"] - (exc_data.trade["entry_atr"]), 2)
                new_pos = ShortPosition(tick["last_price"])
                if exc_data.running_pos is not None:
                    pm.close_position(exc_data.running_pos)
                new_pos_id = pm.new_position(new_pos)
                pm.enter_position(new_pos_id)
                exc_data.running_pos = new_pos_id
                exc_data.running_pos_type = "SHORT"
        msg_obj.usermessages.info(
            f"trade type {exc_data.running_pos_type}, @  {exc_data.trade['entry_price']}, parameter: {exc_data.trade['trade param']}")


def fill_orders2(ticks):  # redo
    global pm, spot_data
    tick_data = None
    for tick in ticks:
        if tick["instrument_token"] == spot_data["instrument_token"]:
            tick_data = tick
    if exc_data.trade_entry:
        exc_data.trade_entry = False
        exc_data.trade["entry_time"] = tick_data["timestamp"]
        exc_data.trade["entry_price"] = tick_data["last_price"]
        if "alt" in exc_data.trade["trade param"]:
            if exc_data.trade["trade action"] == "buy":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.running_pos_type = "LONG"
            elif exc_data.trade["trade action"] == "sell":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"] * 1.5), 2)
                exc_data.running_pos_type = "SHORT"
        else:
            if exc_data.trade["trade action"] == "buy":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"]), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"]), 2)
                exc_data.running_pos_type = "LONG"
            elif exc_data.trade["trade action"] == "sell":
                exc_data.trade["stoploss"] = round(
                    tick_data["last_price"] + (exc_data.trade["entry_atr"]), 2)
                exc_data.trade["target"] = round(
                    tick_data["last_price"] - (exc_data.trade["entry_atr"]), 2)
                exc_data.running_pos_type = "SHORT"
        msg_obj.usermessages.info(
            f"trade type {exc_data.running_pos_type}, @  {exc_data.trade['entry_price']}, parameter: {exc_data.trade['trade param']}")


def system_setup(inputs):  # add proper use of inputs
    """
    populates the global variables
    """
    global instrument_list, expiry, spot_data, pm, IM, chart, psar, st, atr, stoch, pp, \
        data_obj, exc_log, trade_dir, sub_token

    instrument_list = data_obj.instruments(exchange=data_obj.EXCHANGE_NFO)
    expiry = coming_expiry()

    month = expiry.strftime("%b").upper()
    year = expiry.strftime("%y")

    spot_sym = 'BANKNIFTY' + year + month + 'FUT'

    for instru in instrument_list:
        if instru['tradingsymbol'] == spot_sym:
            spot_data = instru
            break

    pm = PositionManager(data_obj)

    # indicator and chart setup
    IM = IndicatorManager(spot_data, data_obj)
    indicators_used = []
    timeframe = 15

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

    exc_log = ExecutionLogic(timeframe=timeframe)

    trade_df = pd.read_csv("resources/ATR_BNF_disc.csv")
    trade_dir = trade_df.to_dict('records')

    exc_log.execution_logic = exc_seq
    sub_token = spot_data["instrument_token"]


def entries():
    global chart, psar, atr, stoch, pp, trade_dir, exc_data

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
                msg_obj.usermessages.info("target reached")
        else:
            if chart.running_cdl["close"] <= exc_data.trade["target"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["target"]
                exc_data.trade["exit_type"] = "target"
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                msg_obj.usermessages.info("target reached")
    return


def stops():
    global msg_obj
    if exc_data.in_trade:
        if exc_data.trade["trade action"] == "buy":
            if chart.running_cdl["close"] <= exc_data.trade["stoploss"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["stoploss"]
                exc_data.trade["exit_type"] = "stoploss"
                msg_obj.usermessages.info("stoploss")
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                exc_data.trade_exit = True
        else:
            if chart.running_cdl["close"] >= exc_data.trade["stoploss"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["stoploss"]
                exc_data.trade["exit_type"] = "stoploss"
                msg_obj.usermessages.info("stoploss")
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                exc_data.trade_exit = True
    return


def eod_exit():
    return


def exc_seq():
    exc_data.trade_exit = False
    eod_exit()
    exits()
    stops()
    if chart.new_candle:
        entries()


# starting execution -----------------
# Initialise
# kws1 = KiteTicker(key_secret[0], data["access_token"])


def on_ticks(ws, ticks):
    # Callback to receive ticks.
    IM.new_ticks(ticks)
    exc_log.execute()
    fill_orders2(ticks)
    if chart.new_candle:
        print("--------------------")


def on_connect(ws, response):
    global sub_token
    print("connection successfully")
    # Callback on successful connect.
    ws.subscribe([sub_token])
    ws.set_mode(ws.MODE_FULL, [sub_token])


def on_close(ws, code, reason):
    # On connection close stop the event loop.
    # Reconnection will not happen after executing `ws.stop()`
    print(f"connection closed {reason}")
    ws.stop()


def on_order_update(ws, data):
    print(data)


# Assign the callbacks.

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
# kws1.connect(threaded=True)

kws1 = None


def ATR_trigger_start(connection_object, data_connection_object, ticker_connection_object, inputs, messaging):
    global data_obj, con_obj, msg_obj, sys_inputs, kws1
    data_obj = data_connection_object
    con_obj = connection_object
    sys_inputs = inputs
    msg_obj = messaging
    system_setup(sys_inputs)
    msg_obj.usermessages.info("Hey ATR is started")
    kws1 = ticker_connection_object
    # ticker_connection_object.close()
    kws1.on_ticks = on_ticks
    kws1.on_connect = on_connect
    kws1.on_close = on_close
    kws1.on_order_update = on_order_update
    kws1.connect(threaded=True)


def ATR_trigger_stop():
    global msg_obj, kws1
    msg_obj.usermessages.info("Stopping things")
    # TODO add square-off funtions
    msg_obj.usermessages.info("perform square-off")
    kws1.stop()

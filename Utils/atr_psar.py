import datetime
import pandas as pd

from Utils.execution_logic import ExecutionLogic
from Utils.indicator_manager import IndicatorManager
from Utils.position_manager import PositionManager
from Utils.positions import Position
import Utils.indicators as indicators


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


class ExecutionData:  # reduce
    def __init__(self):
        self.running_pos = None
        self.running_pos_type = None
        self.prev_close = 0.00
        self.trading = True
        self.can_trade = {"param1": True,
                          "param2": True,
                          "param3": True,
                          "param4": True}
        self.parameter_met = {"param1": False,
                              "param2": False,
                              "param3": False,
                              "param4": False}
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
        self.can_trade = {"param1": True,
                          "param2": True,
                          "param3": True,
                          "param4": True}


data_obj = None
con_obj = None
msg_obj = None
sys_inputs = None
instrument_list = None
expiry = None
spot_data = None

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


def ATR_trigger_start(connection_object, data_connection_object, inputs, messaging):
    global data_obj, con_obj, msg_obj, sys_inputs
    data_obj = data_connection_object
    con_obj = connection_object
    sys_inputs = inputs
    msg_obj = messaging
    system_setup(sys_inputs)
    msg_obj.usermessages.info("Hey ATR is started")


def ATR_trigger_stop():
    global msg_obj
    msg_obj.usermessages.info("Stopping things")


# helper functions
def coming_expiry():    # missing expiry switching
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
        print(
            f"trade entered at {exc_data.trade['entry_time']}, @  {exc_data.trade['entry_price']}")


def system_setup(inputs):  # add proper use of inputs
    """
    populates the global variables
    """
    global instrument_list, expiry, spot_data, pm, IM, chart, psar, st, atr, stoch, pp, \
        data_obj, exc_log, trade_dir

    instrument_list = data_obj.instruments(exchange=data_obj.EXCHANGE_NFO)
    expiry = coming_expiry()

    month = expiry.strftime("%b").upper()
    year = expiry.strftime("%y")

    spot_sym = 'NIFTY' + year + month + 'FUT'

    for instru in instrument_list:
        if instru['tradingsymbol'] == spot_sym:
            spot_data = instru
            break

    pm = PositionManager(data_obj)

    # indicator and chart setup
    IM = IndicatorManager(spot_data, data_obj)
    indicators_used = []
    timeframe = 60

    chart = indicators.CandleSticksChart(timeframe=timeframe)
    psar = indicators.ParabolicSAR(timeframe=timeframe)
    st = indicators.Supertrend(timeframe=timeframe)
    atr = indicators.AverageTrueRange(timeframe=timeframe)
    stoch = indicators.Stochastic(k_length=5, k_smooth=3, d_smooth=3, timeframe=timeframe)
    pp = indicators.PivotPoints()

    indicators_used.append(chart)
    indicators_used.append(psar)
    indicators_used.append(st)
    indicators_used.append(atr)
    indicators_used.append(stoch)
    indicators_used.append(pp)
    IM.add_indicators(indicators_used)

    exc_log = ExecutionLogic(timeframe=timeframe)

    param_list = ["param1", "param1 alt", "param2", "param2 alt",
                  "param3", "param3 alt", "param4", "param4 alt"]
    trade_dir = pd.read_excel("Utils/trade_dis.xlsx", header=[0, 1], sheet_name=param_list)
    for sheet_name in trade_dir:
        trade_dir[sheet_name].set_index((sheet_name, 'pivots'), inplace=True)

    exc_log.execution_logic = exc_seq


def entries():
    global chart, psar, atr, stoch, pp, trade_dir, exc_data

    t_stp = chart.closed_time
    if exc_data.in_trade:
        exc_data.parameter_met = {"param1": False,
                                  "param2": False,
                                  "param3": False,
                                  "param4": False}
        exc_data.trade_entry_copy = False
        return

    if t_stp is None:
        return

    tick_time = (chart.closed_time.hour * 100) + chart.closed_time.minute
    if tick_time >= 1515:
        return
    exc_data.trade = exc_data.trade_temp.copy()
    exc_data.parameter_met = {"param1": False,
                              "param2": False,
                              "param3": False,
                              "param4": False}
    closed = chart.closed_cdl
    candle_size = abs(closed["open"] - closed["close"])

    exc_data.trade_entry_copy = False

    param = ""
    # parameter determinations
    if psar.trend > 0 and st.trend > 0 and exc_data.can_trade["param1"]:
        # PSAR buy ST buy
        if atr.ATR < candle_size:
            param = "param1"
    elif psar.trend < 0 and st.trend > 0 and exc_data.can_trade["param2"]:
        # PSAR sell ST buy
        if atr.ATR < candle_size:
            param = "param2"
    elif psar.trend > 0 and st.trend < 0 and exc_data.can_trade["param3"]:
        # PSAR buy ST sell
        if atr.ATR < candle_size:
            param = "param3"
    elif psar.trend < 0 and st.trend < 0 and exc_data.can_trade["param4"]:
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
    # trade parameter filtering
    final_param = param + alt
    trade_type = trade_dir[final_param].loc[pivot_range][(candle_type, stoch_sig)]

    if trade_type == "no_trade":
        return

    exc_data.trade["trade param"] = final_param
    exc_data.trade["trade action"] = trade_type
    exc_data.trade["entry_atr"] = atr.ATR
    exc_data.trade["candle"] = candle_type
    exc_data.trade["pivot"] = pivot_range
    exc_data.trade["stoch"] = stoch.signal
    exc_data.trade_entry = True
    exc_data.in_trade = True
    exc_data.can_trade[param] = False


def exits():
    if exc_data.in_trade:
        if exc_data.trade["trade action"] == "buy":
            if chart.running_cdl["close"] >= exc_data.trade["target"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["target"]
                exc_data.trade["exit_type"] = "target"
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
        else:
            if chart.running_cdl["close"] <= exc_data.trade["target"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["target"]
                exc_data.trade["exit_type"] = "target"
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
    return


def stops():
    if exc_data.in_trade:
        if exc_data.trade["trade action"] == "buy":
            if chart.running_cdl["close"] <= exc_data.trade["stoploss"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["stoploss"]
                exc_data.trade["exit_type"] = "stoploss"
                exc_data.last_trade = exc_data.trade.copy()
                exc_data.in_trade = False
                exc_data.trade_exit = True
        else:
            if chart.running_cdl["close"] >= exc_data.trade["stoploss"]:
                exc_data.trade["exit_time"] = chart.running_cdl["timestamp"]
                exc_data.trade["exit_price"] = exc_data.trade["stoploss"]
                exc_data.trade["exit_type"] = "stoploss"
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


# # starting execution -----------------
# # Initialise
# kws1 = KiteTicker(key_secret[0], data["access_token"])
#
#
# def on_ticks(ws, ticks):
#     # Callback to receive ticks.
#     IM.new_ticks(ticks)
#     exc_log._execute()
#     fill_orders(ticks)
#     if chart.new_candle:
#         print("--------------------")
#
#
# def on_connect(ws, response):
#     # Callback on successful connect.
#     ws.subscribe(sub_token)
#     ws.set_mode(ws.MODE_FULL, sub_token)
#
#
# def on_close(ws, code, reason):
#     # On connection close stop the event loop.
#     # Reconnection will not happen after executing `ws.stop()`
#     ws.stop()
#
#
# def on_order_update(ws, data):
#     print(data)
#
#
# # Assign the callbacks.
# kws1.on_ticks = on_ticks
# kws1.on_connect = on_connect
# kws1.on_close = on_close
# kws1.on_order_update = on_order_update
# # Infinite loop on the main thread. Nothing after this will run.
# # You have to use the pre-defined callbacks to manage subscriptions.
# kws1.connect(threaded=True)

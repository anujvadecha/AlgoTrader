from collections import namedtuple
from dataclasses import dataclass
# Instrument = namedtuple("Instrument",
#                         ["instrument_token",
#                          "exchange_token",
#                          "tradingsymbol",
#                          "name",
#                          "last_price",
#                          "expiry",
#                          "strike",
#                          "tick_size",
#                          "lot_size",
#                          "instrument_type",
#                          "segment",
#                          "exchange"])
from typing import Any


class Instrument():

    def __init__(self,instrument_token=None,exchange_token=None,tradingsymbol=None,name=None,last_price=None,
                 expiry=None,strike=None,tick_size=None,lot_size=None,instrument_type=None,segment=None,exchange=None,symbol=None):
        if(symbol is None):
            self.instrument_token = instrument_token
            self.exchange_token = exchange_token
            self.tradingsymbol = tradingsymbol
            self.name = name
            self.last_price = last_price
            self.expiry = expiry
            self.strike = strike
            self.tick_size = tick_size
            self.lot_size = lot_size
            self.instrument_type = instrument_type
            self.segment = segment
            self.exchange = exchange
        else:
            from Managers.InstrumentManager import InstrumentManager
            symbolfound = InstrumentManager.get_instance().find_instrument(symbol=symbol)
            self.instrument_token = symbolfound.instrument_token
            self.exchange_token = symbolfound.exchange_token
            self.tradingsymbol = symbolfound.tradingsymbol
            self.name = symbolfound.name
            self.last_price = symbolfound.last_price
            self.expiry = symbolfound.expiry
            self.strike = symbolfound.strike
            self.tick_size = symbolfound.tick_size
            self.lot_size = symbolfound.lot_size
            self.instrument_type = symbolfound.instrument_type
            self.segment = symbolfound.segment
            self.exchange = symbolfound.exchange

    def __str__(self):
        return self.tradingsymbol

@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class Order():
    placed_by:Any=None
    order_id: Any=None
    exchange_order_id: Any=None
    parent_order_id: Any=None
    status: Any=None
    status_message: Any=None
    status_message_raw: Any=None
    order_timestamp: Any=None
    exchange_update_timestamp: Any=None
    exchange_timestamp: Any=None
    variety: Any=None
    exchange: Any=None
    tradingsymbol: Any=None
    instrument_token: Any=None
    order_type: Any=None
    transaction_type: Any=None
    validity: Any=None
    product: Any=None
    quantity: Any=None
    disclosed_quantity: Any=None
    price: Any=None
    trigger_price: Any=None
    average_price: Any=None
    filled_quantity: Any=None
    pending_quantity: Any=None
    cancelled_quantity: Any=None
    market_protection: Any=None
    meta: Any=None
    tag: Any=None
    guid: Any=None


# Order = namedtuple("Order", ['placed_by',
#                              'order_id',
#                              'exchange_order_id',
#                              'parent_order_id',
#                              'status',
#                              'status_message',
#                              'status_message_raw',
#                              'order_timestamp',
#                              'exchange_update_timestamp',
#                              'exchange_timestamp',
#                              'variety',
#                              'exchange',
#                              'tradingsymbol',
#                              'instrument_token',
#                              'order_type',
#                              'transaction_type',
#                              'validity',
#                              'product',
#                              'quantity',
#                              'disclosed_quantity',
#                              'price',
#                              'trigger_price',
#                              'average_price',
#                              'filled_quantity',
#                              'pending_quantity',
#                              'cancelled_quantity',
#                              'market_protection',
#                              'meta', 'tag', 'guid']
#                    )
@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class DisplayOrder():
    order_id:Any
    status: Any
    order_timestamp:Any
    tradingsymbol:Any
    order_type:Any
    transaction_type:Any
    validity:Any
    quantity:Any
    price:Any
    average_price:Any
    filled_quantity:Any
    pending_quantity:Any

@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class DisplayTrade():
    order_id:Any
    order_timestamp:Any
    status:Any
    tradingsymbol:Any
    order_type:Any
    transaction_type:Any
    validity:Any
    quantity:Any
    price:Any
    average_price:Any
    filled_quantity:Any
    pending_quantity:Any

@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class Trade():
   trade_id:Any
   order_id:Any
   exchange:Any
   tradingsymbol:Any
   instrument_token:Any
   product:Any
   average_price:Any
   quantity:Any
   exchange_order_id:Any
   transaction_type:Any
   fill_timestamp:Any
   order_timestamp:Any
   exchange_timestamp:Any

@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class UserMessage():
    Time:Any
    Type:Any
    Message:Any

@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class BrokerMessage():
    Time: Any
    Type: Any
    Message: Any

@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False)
class Tick():
    symbol:Any
    bid:Any
    ask:Any
    bid_qty:Any
    ask_qty:Any
    ltp:Any
    last_qty:Any
    ltt:Any
    average_price:Any
    volume:Any
    buy_quantity:Any
    sell_quantity:Any
    open:Any
    high:Any
    low:Any
    close:Any

Tick = namedtuple("Tick",[
    "symbol","bid","ask","bid_qty","ask_qty","ltp","last_qty","ltt","average_price","volume",
    "buy_quantity","sell_quantity","open","high","low","close"
])

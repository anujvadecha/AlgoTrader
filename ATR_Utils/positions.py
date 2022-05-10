
class Position:
    """
    class used for defining a position

    params:

    """
    # Products
    PRODUCT_MIS = "MIS"           # DEFAULT
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"  # DEFAULT
    ORDER_TYPE_LIMIT = "LIMIT"

    # Varieties
    VARIETY_REGULAR = "regular"   # DEFAULT

    # Validity
    VALIDITY_DAY = "DAY"          # DEFAULT

    # Position Type
    POSITION_TYPE_DAY = "day"     # DEFAULT

    # Trade Type
    TYPE_LONG = "LONG"            # DEFAULT
    TYPE_SHORT = "SHORT"

    # Transaction type
    __TRANSACTION_TYPE_BUY = "BUY"
    __TRANSACTION_TYPE_SELL = "SELL"

    # Status Type
    __STATUS_CREATED = "CREATED"
    __STATUS_PLACED_EN = "PLACED_EN"
    __STATUS_PLACED_EX = "PLACED_EX"
    __STATUS_RUNNING = "RUNNING"
    __STATUS_CLOSED = "CLOSED"

    def __init__(self, symbol_data, trade_type, quantity, product=None, validity=None, disclosed_quantity=None):
        self.broker = None
        self.UID = None
        self.symbol_data = symbol_data
        self.exchange = symbol_data["exchange"]
        self.trade_type = trade_type
        self.quantity = quantity
        self.disclosed_quantity = disclosed_quantity
        if product is None:
            self.product = Position.PRODUCT_MIS
        else:
            self.product = product
        if validity is None:
            self.validity = Position.VALIDITY_DAY
        else:
            self.validity = validity
        self.disclosed_quantity = disclosed_quantity
        self.status = Position.__STATUS_CREATED

        self.LTP = 0.00
        self.entry_quantity = None
        self.entry_price = 0.00
        self.running_quantity = None
        self.running_PNL = 0
        self.exit_price = None                   # needs better implementation for multiple exits

    def assign_uid(self, received_uid):
        self.UID = received_uid

    def enter(self, broker, order_type=None, price=None):
        self.broker = broker
        if order_type is None:
            order_type = Position.ORDER_TYPE_MARKET

        if self.trade_type is Position.TYPE_LONG:
            order_id = self.broker.place_order(variety=Position.VARIETY_REGULAR,
                                               tradingsymbol=self.symbol_data["tradingsymbol"],
                                               exchange=self.exchange,
                                               transaction_type=Position.__TRANSACTION_TYPE_BUY,
                                               quantity=self.quantity,
                                               order_type=order_type,
                                               price=price,
                                               product=self.product,
                                               validity=Position.VALIDITY_DAY,
                                               tag=self.UID,
                                               disclosed_quantity=self.disclosed_quantity,
                                               trigger_price=None,
                                               squareoff=None,
                                               stoploss=None,
                                               trailing_stoploss=None)
            self.status = Position.__STATUS_PLACED_EN
        else:
            order_id = self.broker.place_order(variety=Position.VARIETY_REGULAR,
                                               tradingsymbol=self.symbol_data["tradingsymbol"],
                                               exchange=self.exchange,
                                               transaction_type=Position.__TRANSACTION_TYPE_SELL,
                                               quantity=self.quantity,
                                               order_type=order_type,
                                               product=self.product,
                                               price=price,
                                               validity=Position.VALIDITY_DAY,
                                               tag=self.UID,
                                               disclosed_quantity=self.disclosed_quantity,
                                               trigger_price=None,
                                               squareoff=None,
                                               stoploss=None,
                                               trailing_stoploss=None)
            self.status = Position.__STATUS_PLACED_EN

        # change implementation
        self.running_quantity = self.quantity
        self.entry_quantity = self.quantity
        return order_id

    def exit(self, quantity=None, order_type=None, price=None):
        if order_type is None:
            order_type = Position.ORDER_TYPE_MARKET

        if quantity is None:
            quantity = self.running_quantity
        self.running_quantity -= quantity
        if self.trade_type is Position.TYPE_LONG:
            order_id = self.broker.place_order(variety=Position.VARIETY_REGULAR,
                                               tradingsymbol=self.symbol_data["tradingsymbol"],
                                               exchange=self.exchange,
                                               transaction_type=Position.__TRANSACTION_TYPE_SELL,
                                               quantity=quantity,
                                               order_type=order_type,
                                               price=price,
                                               product=self.product,
                                               validity=Position.VALIDITY_DAY,
                                               tag=self.UID,
                                               disclosed_quantity=self.disclosed_quantity,
                                               trigger_price=None,
                                               squareoff=None,
                                               stoploss=None,
                                               trailing_stoploss=None)
            self.status = Position.__STATUS_PLACED_EX
            return order_id
        else:
            order_id = self.broker.place_order(variety=Position.VARIETY_REGULAR,
                                               tradingsymbol=self.symbol_data["tradingsymbol"],
                                               exchange=self.exchange,
                                               transaction_type=Position.__TRANSACTION_TYPE_BUY,
                                               quantity=quantity,
                                               order_type=order_type,
                                               price=price,
                                               product=self.product,
                                               validity=Position.VALIDITY_DAY,
                                               tag=self.UID,
                                               disclosed_quantity=self.disclosed_quantity,
                                               trigger_price=None,
                                               squareoff=None,
                                               stoploss=None,
                                               trailing_stoploss=None)
            self.status = Position.__STATUS_PLACED_EX
            return order_id

    def confirm_entry(self):
        """
        NOT IMPLEMENTED (URGENT)
        """
        return

    def confirm_exit(self):
        """
        NOT IMPLEMENTED
        """
        return

    def risk_setup(self):
        """
        NOT IMPLEMENTED
        """
        return

    def risk_management(self):
        """
        NOT IMPLEMENTED
        """
        return

    def __update_pnl(self, tick):
        """
        NOT IMPLEMENTED
        """
        return

    def _new_tick(self, ticks):
        """
        NOT IMPLEMENTED
        """
        tick_data = None
        for tick in ticks:
            if tick["instrument_token"] == self.symbol_data["instrument_token"]:
                tick_data = tick
                break
        self.__update_pnl(tick_data)



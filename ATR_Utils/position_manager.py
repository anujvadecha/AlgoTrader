class PositionManager:
    """
    class used for trade management

    params:

    """

    def __init__(self, broker):
        self.broker = broker
        self.position_book_created = {}
        self.position_counter = 0
        self.open_positions = 0
        self.position_book_closed = {}
        self.position_book_opened = {}

    def new_position(self, position):
        self.position_counter += 1
        position.assign_uid(str(self.position_counter))
        self.position_book_created[str(self.position_counter)] = position
        print(f'new position {self.position_counter} of type {position.trade_type}')
        return str(self.position_counter)

    def enter_position(self, uid, order_type=None, price=None):
        self.position_book_created[uid].enter(self.broker, order_type, price)
        self.position_book_opened[uid] = self.position_book_created[uid]
        print(f'entered position {uid} of type {self.position_book_opened[uid].trade_type}')
        return

    def exit_position(self, uid, quantity=None, order_type=None, price=None):
        if self.position_book_opened[uid].running_quantity <= quantity:
            self.close_position(uid, order_type=None, price=None)
            return
        if quantity is None:
            self.close_position(uid, order_type=None, price=None)
            return
        self.position_book_opened[uid].exit(quantity, order_type, price)
        print(
            f'exited qty {quantity} position {uid} of type {self.position_book_opened[uid].trade_type}')
        return

    def close_position(self, uid, order_type=None, price=None):
        self.position_book_opened[uid].exit(order_type, price)
        self.position_book_closed[uid] = self.position_book_opened[uid]
        del self.position_book_opened[uid]
        print(f'closed position {uid} of type {self.position_book_closed[uid].trade_type}')
        return

    def close_all(self):
        for position in self.position_book_opened:
            self.position_book_opened[position].exit(position)
        return

    def new_tick(self, ticks):
        """
        NOT IMPLEMENTED
        """
        for position in self.position_book_opened:
            self.position_book_opened[position].new_tick(ticks)
        return

    def new_update(self, update):
        """
        NOT IMPLEMENTED
        """
        return

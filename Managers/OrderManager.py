from queue import Queue

# Maintains a dictionary of orders to keep track and update totalPNL

class OrderManager():
    # TODO Get this to work
    order_map = {}
    order_updates = Queue(maxsize=200)

    def add_order(self,order):
        self.order_map[order["order_id"]] = order

    def process_order_updates(self):
        while not self.order_updates.empty():
            order=self.order_updates.get()
            if order["order_id"] in self.order_map.keys():
                self.order_map["order_id"] = order
        raise NotImplementedError

    def put_order_update(self,order_update):
        self.order_updates.put(order_update)

    __instance = None

    @staticmethod
    def get_instance():
        if OrderManager.__instance == None:
            OrderManager()
        return OrderManager.__instance

    def __init__(self):
        if OrderManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            OrderManager.__instance = self

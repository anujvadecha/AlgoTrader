import threading
import time

import schedule

from MessageClasses import Messages


class StrategyManager():

    latest_portfolio_id = 0
    strategy_map = {}

    def add_strategy(self,strategy):
       self.latest_portfolio_id += 1
       strategy.portfolio_id=self.latest_portfolio_id
       self.strategy_map[self.latest_portfolio_id] = strategy

    def schedule_thread(self):
        while True:
            schedule.run_pending()
            time.sleep(0.5)

    def start_schedule_thread(self):
        threading.Thread(target=self.schedule_thread).start()

    def start_strategy(self,strategy,inputs):
        threading.Thread(target=strategy.main,args=[inputs]).start()
        Messages.getInstance().usermessages.info("STARTING STARTEGY "+str(strategy.__class__) +" INPUTS "+ str(inputs) )

    def stop_strategy(self, portfolio_id):
        self.strategy_map[int(portfolio_id)].stop()

    __instance = None

    @staticmethod
    def get_instance():
        if StrategyManager.__instance == None:
            StrategyManager()
        return StrategyManager.__instance

    def __init__(self):
        if StrategyManager.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            StrategyManager.__instance = self
            self.start_schedule_thread()

from ATR_Utils.indicators import Indicator


class ExecutionLogic:
    """
    class responsible for the execution of system logic

    params:

    """

    def __init__(self, timeframe=1, exc_trigger="tick"):
        self.position_manager = None
        self.indicator = Indicator(exc_trigger, timeframe)  # used for syncing with charts
        self.execution_logic = None

    def execute(self):
        self.execution_logic()
        return

    def assign_position_manager(self, pos_man):
        self.position_manager = pos_man
        return

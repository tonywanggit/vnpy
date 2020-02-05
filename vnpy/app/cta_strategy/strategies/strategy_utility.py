from vnpy.app.cta_strategy import (
    ArrayManager
)

import talib

class AdvanceArrayManager(ArrayManager):

    def __init__(self, size=100):
        super().__init__(size)

    def ma(self, n, array=False):
        """
        Moving average.
        """
        result = talib.MA(self.close, n)
        if array:
            return result
        return result[-1]

    def boll_double_up(self, n, entry_dev, exit_dev, array=False):
        """
        Bollinger Channel.
        """
        mid = self.ma(n, array)
        std = self.std(n, array)

        entry_up = mid + std * entry_dev
        exit_up = mid + std * exit_dev

        return entry_up, exit_up

    def boll_double_down(self, n, entry_dev, exit_dev, array=False):
        """
        Bollinger Channel.
        """
        mid = self.ma(n, array)
        std = self.std(n, array)

        entry_up = mid - std * entry_dev
        exit_up = mid - std * exit_dev

        return entry_up, exit_up
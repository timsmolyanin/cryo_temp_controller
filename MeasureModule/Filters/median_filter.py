from Filters import Filter
from statistics import median

class Median(Filter):
    def __init__(self, buffer):
        super().__init__(buffer)

    def filtering(self) -> float:
        return median(self.window)
from Filters import Filter
from statistics import median

class Median(Filter):
    def __init__(self, buffer_size):
        super().__init__(buffer_size)

    def filter_value(self, value:float) -> float:
        super().filter_value(value)
        return median(self.buffer)
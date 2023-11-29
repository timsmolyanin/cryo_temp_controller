from Filters import Filter

class MovingAverage(Filter):
    def __init__(self, buffer_size):
        super().__init__(buffer_size)

    def filter_value(self, value) -> float:
        super().filter_value(value)
        return sum(self.buffer)/len(self.buffer)

from Filters import Filter

class MovingAverage(Filter):
    def __init__(self, buffer):
        super().__init__(buffer)

    def filtering(self) -> float:
        return sum(self.window)/len(self.window)

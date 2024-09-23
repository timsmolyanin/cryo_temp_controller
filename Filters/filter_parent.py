from abc import ABC, abstractmethod

class Filter(ABC):
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.buffer = list()

    @abstractmethod
    def filter_value(self, value:float) -> float:
        self.add_value(value)


    def change_buffer_size(self, new_buffer_size : int) -> None:
        if new_buffer_size < self.buffer_size:
            self.buffer = self.buffer[self.buffer_size-new_buffer_size::] 
        self.buffer_size = new_buffer_size


    def add_value(self, value : float) -> None:
        if len(self.buffer) >= self.buffer_size:
            self.buffer = self.buffer[1:self.buffer_size:]
        self.buffer.append(value)


    def clear(self):
        self.buffer = list()
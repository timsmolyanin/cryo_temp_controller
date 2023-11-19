from abc import ABC, abstractmethod

class Filter(ABC):
    def __init__(self, buffer):
        self.buffer = buffer
        self.window = list()

    @abstractmethod
    def filtering(self) -> float:
        pass

    def change_buffer(self, buffer : int) -> None:
        if buffer < self.buffer:
            self.window = self.window[self.buffer-buffer::] 
        self.buffer = buffer

    def add_value(self, value : float) -> None:
        if len(self.window) >= self.buffer:
            self.window = self.window[1:self.buffer:]
        self.window.append(value)

    def clear(self):
        self.window = list()
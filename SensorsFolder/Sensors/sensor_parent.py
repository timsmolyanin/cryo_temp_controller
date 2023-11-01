from abc import ABC, abstractmethod
from enum import Enum

def error_print(msg):
    print(msg)

class Sensor(ABC):
    def __init__(self, path=None, current=0):
        self.config = list()
        self.event_error = error_print
        self.current = current
        self.type = SensorType.NONE
        if path != None:
            self.load_config(path)

    @abstractmethod
    def load_config(self, path : str):
        print("load_config: " + path)
        pass

    @abstractmethod
    def convert(self, value : float) -> float:
        pass

    @abstractmethod
    def convert_to_C(self, voltage : float) -> float:
        pass

    def convert_K_to_C(self, temperature : float) -> float:
        return temperature - 273.15
    
    def convert_C_to_K(self, temperature : float) -> float:
        return temperature + 273.15



class SensorType(Enum):
    NONE = 0
    RESISTANCE = 1
    VOLTAGE = 2
    


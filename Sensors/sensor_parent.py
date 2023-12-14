from abc import ABC, abstractmethod
from enum import Enum

class Sensor(ABC):
    def __init__(self, path=None, current=0):
        self.config_file_extentions = ['txt']
        self.current = current
        self.type = SensorType.NONE
        if path != None:
            self.load_config(path)
        self.name = "sensor"


    @abstractmethod
    def load_config(self, path : str):
        self.config = {}
        if path.split('.')[-1] not in self.config_file_extentions:
            raise FileNotFoundError(f'config file {path} has wrong extention, expected {self.config_file_extentions}')


    @abstractmethod
    def convert(self, value : float) -> float:
        raise AttributeError('Sensor is not initialized')


    @abstractmethod
    def convert_to_C(self, voltage : float) -> float:
        raise AttributeError('Sensor is not initialized')


    def convert_K_to_C(self, temperature : float) -> float:
        return temperature - 273.15
    

    def convert_C_to_K(self, temperature : float) -> float:
        return temperature + 273.15


class SensorType(Enum):
    NONE = 0
    RESISTANCE = 1
    VOLTAGE = 2

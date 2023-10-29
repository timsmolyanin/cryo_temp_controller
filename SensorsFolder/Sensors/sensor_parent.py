from abc import ABC, abstractmethod

class Sensor(ABC):
    def __init__(self, path : str):
        self.config = list()
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
    


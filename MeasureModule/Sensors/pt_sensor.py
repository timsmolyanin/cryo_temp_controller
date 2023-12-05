from Sensors import Sensor
from Sensors import SensorType
from math import sqrt
from loguru import logger
import sys

class PtSensor(Sensor):
    def __init__(self, path=None, current=45):
        super().__init__(path, current)
        self.type = SensorType.RESISTANCE
        self.config_file_extention = ['txt']


    def load_config(self, path : str):
        """
            Load config table 
        """
        try:
            super().load_config(path)
            file = open(path)
            self.config = {i.split()[0] : float(i.split()[1]) for i in file.read().split('\n')}
            file.close()
        except Exception as err:
            raise type(err)(f'Error while loading config: {err}')


    def convert(self, resistance : float) -> float:
        """
            Get voltage.

            Return value in Kelvin.

            If voltage > max limit or voltage < min limit, return Exeption(`Uncorrect voltage`). 
        """
        

        return self.convert_C_to_K(self.convert_to_C(resistance))
    
    def convert_to_C(self, resistance : float) -> float:
        try:
            if len(self.config) == 0:
                raise AttributeError('Config is empty')
            temperature = -self.config["R0"] * self.config["A"]
            try:
                temperature += sqrt(self.config["R0"]**2 * self.config["A"]**2 - 4 * self.config["R0"] * self.config["B"] * (self.config["R0"] - resistance))
            except ValueError:
                raise ValueError('Attemted sqrt(k<0). Invalid input value or sensor config.')
            temperature /= 2 * self.config["R0"] * self.config["B"]
            return temperature
        except Exception as err:
            raise type(err)(f'Error while converting: {err}')
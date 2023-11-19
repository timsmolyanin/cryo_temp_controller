from Sensors import Sensor
from Sensors import SensorType
from math import sqrt
from loguru import logger
import sys
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class PtSensor(Sensor):
    def __init__(self, path=None, current=45):
        super().__init__(path, current)
        self.type = SensorType.RESISTANCE

    def load_config(self, path : str):
        """
            Load config table 
        """
        try:
            file = open(path)
            self.config = {i.split()[0] : float(i.split()[1]) for i in file.read().split('\n')}
            file.close()
            logger.debug("Config Load")
        except Exception as e:
            self.event_error(f"Config not loading. Exeption: {e}")


    def convert(self, resistance : float) -> float:
        """
            Get voltage.

            Return value in Kelvin.

            If voltage > max limit or voltage < min limit, return Exeption(`Uncorrect voltage`). 
        """
        

        return self.convert_C_to_K(self.convert_to_C(resistance))
    
    def convert_to_C(self, resistance : float) -> float:
        if len(self.config) == 0:
            self.event_error("Config is empty")

        temperature = -self.config["R0"] * self.config["A"]
        try:
            temperature += sqrt(self.config["R0"]**2 * self.config["A"]**2 - 4 * self.config["R0"] * self.config["B"] * (self.config["R0"] - resistance))
        except Exception as e:
            self.event_error("The resistance is too big")
            return -274.15
        temperature /= 2 * self.config["R0"] * self.config["B"]
        return temperature
from Sensors import Sensor
from Sensors import SensorType
from math import sqrt
from loguru import logger
import sys
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class PtSensor(Sensor):
    def __init__(self, path="", id=45):
        super().__init__(path, id)
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
            self.event_error(e)
            logger.exception(f"Config not loading. Exeption: {e}")


    def convert(self, resistance : float) -> float:
        """
            Get voltage.

            Return value in Kelvin.

            If voltage > max limit or voltage < min limit, return Exeption(`Uncorrect voltage`). 
        """
        return self.convert_C_to_K(self.convert_to_C(resistance))
    
    def convert_to_C(self, resistance : float) -> float:
        if len(self.config) == 0:
            logger.exception("Config is empty")
            raise Exception("Config is empty")

        temperature = -(sqrt((self.config["k1"] * resistance) + self.config["k2"]) - self.config["k3"]) / self.config["k4"]

        return temperature
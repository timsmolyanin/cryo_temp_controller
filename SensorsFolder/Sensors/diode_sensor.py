from Sensors import Sensor
from loguru import logger
import sys
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class DiodeSensor(Sensor):
    def __init__(self, path):
        super().__init__(path)

    def load_config(self, path : str):
        """
            Load config table 
        """
        try:
            file = open(path)
            self.config = {float(i.split()[1]) : float(i.split()[2]) for i in file.read().split('\n')[1::]}
            file.close()
            logger.debug("Config Load")
        except:
            logger.exception("Config not loading. Exeption: {}")


    def convert(self, voltage : float) -> float:
        """
            Get voltage.

            Return value in Kelvin.

            If voltage > max limit or voltage < min limit, return Exception(`Incorrect voltage`). 
        """

        if len(self.config) == 0:
            logger.exception("Config is empty")
            raise Exception("Config is empty")

        if voltage < list(self.config.keys())[0]:
            raise Exception("Voltage less min limit sensor")
        
        if voltage > list(self.config.keys())[-1]:
            raise Exception("Voltage more max limit sensor")

        temperature = -1
        prev = 0
        for key in self.config:
            if key > voltage:

                k = (self.config[key] - self.config[prev])/(key - prev)
                b = self.config[key] - k * key
                temperature = (k * voltage + b)
                
                break
            prev = key
        
        return temperature
    
    def convert_to_C(self, voltage : float) -> float:
        temperature = self.convert(voltage)
        return self.convert_K_to_C(temperature)
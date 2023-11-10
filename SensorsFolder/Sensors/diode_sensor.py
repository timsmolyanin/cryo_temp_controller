from Sensors import Sensor
from Sensors import SensorType
from loguru import logger
import sys
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class DiodeSensor(Sensor):
    def __init__(self, path=None, current=100):
        super().__init__(path, current)
        self.type = SensorType.VOLTAGE

    def load_config(self, path : str):
        """
            Load config table 
        """
        try:
            file = open(path)
            self.config = {float(i.split()[1]) : float(i.split()[2]) for i in file.read().split('\n')[1::]}
            file.close()
            logger.debug("Config Load")
        except Exception as e:
            self.event_error(e)
            logger.exception(f"Config not loading. Exeption: {e}")


    def convert(self, voltage : float) -> float:
        """
            Get voltage.

            Return value in Kelvin.

            If voltage > max limit or voltage < min limit, return Exception(`Incorrect voltage`). 
        """

        voltage /=1000 # V to mV

        if len(self.config) == 0:
            logger.exception("Config is empty")
            self.event_error("Config is empty")
            return

        if voltage < list(self.config.keys())[0]:
            self.event_error("Voltage less min limit sensor")
            return
        
        if voltage > list(self.config.keys())[-1]:
            self.event_error("Voltage more max limit sensor")
            return

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
    
from Sensors import Sensor
from loguru import logger
from scipy.optimize import curve_fit
import numpy as np
import sys
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class DiodeSensor(Sensor):
    def __init__(self, path, func_type="liner"):
        super().__init__(path)
        self.func_type = func_type
        if self.func_type == "approx":
            self.approximation()

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
        if self.func_type == "liner":
            prev = 0
            for key in self.config:
                if key > voltage:

                    k = (self.config[key] - self.config[prev])/(key - prev)
                    b = self.config[key] - k * key
                    temperature = (k * voltage + b)
                    
                    break
                prev = key
        else:
            temperature = self.func(voltage, *self.popt)
        
        return temperature
    
    def convert_to_C(self, voltage : float) -> float:
        temperature = self.convert(voltage)
        return self.convert_K_to_C(temperature)


    def approximation(self):
        self.func = self.function_approx
        self.popt, self.pcov = curve_fit(self.func, list(self.config.keys()), list(self.config.values()))

    def function_approx(self, x, a, b, c, d, f, g, n) -> float:
        return a * x**6 + b * x**5 + c * x**4 + d * x**3 + g * x**2 + f * x + n
    
    def liner_function(self, x, a, b) -> float:
        return a * x + b
    
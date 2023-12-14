from Sensors import Sensor
from Sensors import SensorType

class DiodeSensor(Sensor):
    def __init__(self, path=None, current=100):
        super().__init__(path, current)
        self.type = SensorType.VOLTAGE
        self.config_file_extentions = ['340']


    def load_config(self, path : str):
        """
            Load config table 
        """
        try:
            super().load_config(path)
            with open(path) as file:
                for cur_line in file.readlines()[9:]:
                    cur_line = cur_line.split()
                    self.config.update({float(cur_line[1]) : float(cur_line[2])})
        except Exception as err:
            raise type(err)(f'Error while loading config: {err}')


    def convert(self, voltage : float) -> float:
        """
            Get voltage.

            Return value in Kelvin.

            If voltage > max limit or voltage < min limit, return Exception(`Incorrect voltage`). 
        """

        try:
            voltage /=1000 # mV to V
            if len(self.config) == 0:
                raise AttributeError('Config is empty')

            if voltage < list(self.config.keys())[0] or voltage > list(self.config.keys())[-1]:
                raise ValueError(f'Input value is outside of acceptable sensor range')
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
        except Exception as err:
            raise type(err)(f'Error while converting: {err}')
    

    def convert_to_C(self, voltage : float) -> float:
        temperature = self.convert(voltage)
        return self.convert_K_to_C(temperature)
    
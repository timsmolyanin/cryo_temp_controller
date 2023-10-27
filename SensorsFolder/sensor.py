import matplotlib.pyplot as plt
from loguru import logger
import sys
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class Sensor():
    def __init__(self, path, step = 3, is_voltage_positive_coefficient = False):
        self.config = list()
        self.is_voltage_positive_coefficient = is_voltage_positive_coefficient
        self.load_config(path)

        self.start_index = 0
        self.end_index = len(self.config)
        self.step = step

    
    @property
    def start_line_config(self) -> int:
        return self.start_index
    
    @start_line_config.setter
    def start_line_config(self, value):
        self.start_index = value if value > 0 else 0

    @property
    def end_line_config(self) -> int:
        return self.end_index
    
    @end_line_config.setter
    def end_line_config(self, value):
        self.end_index = value if value < len(self.config) else len(self.config)


    def load_config(self, path : str):
        """
            Load config table 
        """
        try:
            file = open(path)
            self.config = [list(map(float, i.split())) for i in file.read().split('\n')[1::]]
            file.close()
            logger.debug("Config Load")
        except:
            logger.exception("Config not loading. Exeption: {}")
        
        if self.is_voltage_positive_coefficient:
            self.config.reverse()

    def convert(self, voltage : float) -> float:
        """
            Get voltage.

            Return value in Kelvin.

            If voltage > max limit or voltage < min limit, return Exeption(`Uncorrect voltage`). 
        """

        if len(self.config) == 0:
            logger.exception("Config is empty")
            raise Exception("Config is empty")
        
        if voltage < self.config[self.start_line_config][1]:
            self.start_line_config = 0
        elif voltage > self.config[self.end_line_config-1][1]:
            self.end_line_config = len(self.config)

        temperature = -1
        area = self.config[self.start_line_config:self.end_line_config:]
        prev = area[0]
        index = self.start_line_config
        for i in area:
            if i[1] > voltage:
                self.start_line_config = index - self.step
                self.end_line_config = index + self.step

                k = (i[2] - prev[2])/(i[1] - prev[1])
                b = i[2] - k * i[1]
                temperature = (k * voltage + b)
                
                break

            index += 1
            prev = i
        
        return temperature
        
    def convert_K_to_C(self, temperature : float) -> float:
        return temperature - 273,15
    
    def convert_V_to_C(self, voltage : float) -> float:
        return self.convert_K_to_C(self.convert(voltage))


def main():
    logger.info("Test sensor converter")
    
    sensor = Sensor('SensorsFolder/diodChine.txt')

    # 
    # Create graf
    # 
    # n = 500
    # x = sensor.max_limit
    # step = (x - sensor.min_limit)/n
    # X = []
    # Y = []
    # for i in range(n):
    #     Y.append(x)
    #     X.append(sensor.convert(x))
    #     x -= step
    # logger.info(x)
    # plt.plot(X, Y)
    # plt.show()

    # 
    # Input voltage
    # 
    while True:
        try:
            volt = float(input("Voltage: "))
            if volt == -1:
                break
            print(sensor.convert(volt))
        except:
            pass


if __name__ == "__main__":
    main()
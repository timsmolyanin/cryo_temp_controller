from Sensors import *
from matplotlib import pyplot as plt

def main():    
    #sensor1 = DiodeSensor("SensorsFolder\Sensors\ConfigFolder\diode2.txt", "approx")
    # 
    # Create graf
    # 

    # file = open("SensorsFolder\Sensors\ConfigFolder\diode2.txt")
    # config = {float(i.split()[1]) : float(i.split()[2]) for i in file.read().split('\n')[1::]}
    # file.close()

    # n = 500
    # # x = list(sensor1.config.keys())[-1]
    # # step = (x - list(sensor1.config.keys())[0])/n
    # # X = []
    # # Y = []
    # # for i in range(n):
    # #     Y.append(x)
    # #     X.append(sensor1.convert(x))
    # #     x -= step
    # # plt.plot(X, Y)

    # sensor2 = DiodeSensor("SensorsFolder\Sensors\ConfigFolder\diode2.txt")
    # x = list(sensor2.config.keys())[-1]
    # step = (x - list(sensor2.config.keys())[0])/n
    # X = []
    # Y = []  
    # for i in range(n):
    #     Y.append(x)
    #     X.append(sensor2.convert(x))
    #     x -= step
    # plt.plot(X, Y)

    # X = []
    # Y = []
    # for i in list(config.keys()):
    #     Y.append(i)
    #     X.append(config[i])
    # plt.plot(X, Y, "ro", markersize=2)


    # plt.show()

    # 
    # Input voltage
    # 
    while True:
        inp = input("Value: ")
        if inp == "pt100":
            sensor = PtSensor("SensorsFolder\Sensors\ConfigFolder\pt100_config.txt")
        elif inp == "pt1000":
            sensor = PtSensor("SensorsFolder\Sensors\ConfigFolder\pt1000_config_2.txt")
        elif inp == "diod_liner":
            sensor = DiodeSensor("SensorsFolder\Sensors\ConfigFolder\diode2.txt")
        else:
            try:
                print(sensor.convert(float(inp)))
            except Exception as err:
                print(err)


if __name__ == "__main__":
    main()
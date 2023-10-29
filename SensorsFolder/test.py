from Sensors import *

def main():    
    sensor = None
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
        inp = input("Value: ")
        if inp == "diod":
            sensor = DiodeSensor("SensorsFolder\Sensors\ConfigFolder\diodChine.txt")
        elif inp == "pt1000":
            sensor = PtSensor("SensorsFolder\Sensors\ConfigFolder\pt1000_config.txt")
        else:
            try:
                print(sensor.convert(float(inp)))
            except Exception as err:
                print(err)


if __name__ == "__main__":
    main()
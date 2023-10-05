
import math
import paho.mqtt.publish as publish
import statistics


heater_on_cmds = ["mesurments.q0.picc=18", "mesurments.b3.picc=18", "mesurments.t12.picc=16",
                  "mesurments.t13.picc=16", "mesurments.t14.picc=16", "mesurments.t15.picc=16",
                  "mesurments.t16.picc=16", "mesurments.t12.pco=0", "mesurments.t13.pco=0",
                  "mesurments.t14.pco=0", "mesurments.t15.pco=0", "mesurments.t16.pco=0",
                  "mesurments.t17.pco=0", "mesurments.t18.pco=0", "mesurments.t19.pco=0",
                  "mesurments.b3.picc2=19"]

heater_off_cmds = ["mesurments.q0.picc=20", "mesurments.b3.picc=20", "mesurments.t12.picc=20",
                  "mesurments.t13.picc=16", "mesurments.t14.picc=17", "mesurments.t15.picc=16",
                  "mesurments.t16.picc=17", "mesurments.t12.pco=50744", "mesurments.t13.pco=50744",
                  "mesurments.t14.pco=50744", "mesurments.t15.pco=50744", "mesurments.t16.pco=50744",
                  "mesurments.t17.pco=50744", "mesurments.t18.pco=50744", "mesurments.t19.pco=50744",
                  "mesurments.b3.picc2=21"]

ch1_current_off_cmds = ["mesurments.t6.picc=15", "mesurments.t6.pco=50744", "mesurments.t0.picc=13",
                        "mesurments.t0.pco=50744", "mesurments.t7.picc=14", "mesurments.t7.pco=50744",
                        "mesurments.t10.pco=50744", "mesurments.t4.pco=50744", "mesurments.t1.pco=50744",
                        "mesurments.t1.picc=12"]

ch1_current_on_cmds = ["mesurments.t6.picc=14", "mesurments.t6.pco=13765", "mesurments.t0.picc=12", 
                       "mesurments.t0.pco=31", "mesurments.t7.picc=14", "mesurments.t7.pco=13765",
                       "mesurments.t10.pco=13765", "mesurments.t4.pco=31", "mesurments.t1.pco=31",
                        "mesurments.t1.picc=12"]

ch2_current_off_cmds = ["mesurments.t8.picc=15", "mesurments.t8.pco=50744", "mesurments.t2.picc=13",
                        "mesurments.t2.pco=50744", "mesurments.t9.picc=14", "mesurments.t9.pco=50744",
                        "mesurments.t11.pco=50744", "mesurments.t5.pco=50744"]


ch2_current_on_cmds = ["mesurments.t8.picc=14", "mesurments.t8.pco=13765", "mesurments.t2.picc=12",
                       "mesurments.t2.pco=31", "mesurments.t9.picc=14", "mesurments.t9.pco=13765",
                        "mesurments.t11.pco=13765", "mesurments.t5.pco=31"]


def calculate_moving_average(var_list, buffer_size: int, mqtt_host: str, topic: str):
    sma = 0
    tmp = 0
    mov_av_list = var_list
    buffer_size_value = buffer_size
    for val in mov_av_list:
        tmp = tmp + val
    sma = round(tmp / buffer_size_value, 4)
    mov_av_list = list()
    publish.single(topic, str(sma), hostname=mqtt_host)
        
    

def calculate_median(var_list, buffer_size: int, value: float, mqtt_host: str, topic: str):
    median = 0
    tmp = 0
    median_list = var_list
    buffer_size_value = buffer_size
    median_list.append(value)
    if len(median_list) == buffer_size_value:
        median = round(statistics.median(median_list), 4)
        publish.single(topic, str(median), hostname=mqtt_host)
        median_list = list()


def convert_resistanc_to_temp(resistance: float) -> list:
    k1 = -0.00232
    k2 = 17.59246
    k3 = 3.908
    k4 = 0.00116
    temp_celcius = -(math.sqrt((k1 * resistance) + k2) - k3) / k4
    temp_kelvin = temp_celcius + 273.15

    return round(temp_celcius, 2), round(temp_kelvin, 2)


def switch_heater_state(state: int):
    mqtt_host = "192.168.44.11"
    if isinstance(state, int):
        topic = "/devices/HeaterModule/controls/Output Voltage State/on"
        publish.single(topic, str(state), hostname=mqtt_host)


def set_current_counts(counts: int):
    mqtt_host = "192.168.44.11"
    if isinstance(counts, int):
        topic = "/devices/MeasureModule/controls/CH2 DAC/on"
        publish.single(topic, str(counts), hostname=mqtt_host)


def set_heater_voltage(setpoint: int, rate: int):
    pass
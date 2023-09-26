
import math
import paho.mqtt.publish as publish


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

import time
import system_module
from nextion_mqtt_bridge import NextionMqttBridge
from MeasureModule import MeasureModule, HeaterConverter
from pid_control import PIDControl
from list_of_mqtt_topics import list_of_mqtt_topics, mqtt_topics_current_ch1_pid, mqtt_topics_current_ch2_pid, mqtt_topics_heater_pid, mqtt_topics_system_module



def create_modules():
        #TODO: read config with cryo_control channel configuration
        broker = "127.0.0.1"
        port = 1883
    
        ch1_module = MeasureModule(broker=broker, port=port, channel_number=1)
        ch1_module.start()
    
        ch2_module = MeasureModule(broker=broker, port=port, channel_number=2)
        ch2_module.start()
    
        ch1_heater = HeaterConverter(broker=broker, port=port, channel_number=1)
        ch1_heater.start()


def main():

    mqtt_broker = "127.0.0.1"
    mqtt_port = 1883
    # mqtt_user = "admin"
    # mqtt_password = "admin"
    comport = "/dev/ttyS4"
    baudrate = 115200

    display_mqtt_bridge = NextionMqttBridge(mqtt_port=mqtt_port, mqtt_broker=mqtt_broker, mqtt_passw=None, mqtt_user=None,
                                            comport_baudrate=baudrate, comport_name=comport)
    display_mqtt_bridge.start()
    display_mqtt_bridge.mqtt_start()

    create_modules()

    pid_current_ch1_test = PIDControl(mqtt_topics_current_ch1_pid, mqtt_broker, mqtt_port, mqtt_user=None, mqtt_password=None, pid_max_range=65535, ki=15.8764268160044748, kd=0.9, kp=15.24685919461204)
    pid_current_ch1_test.set_pid_limits_min(0)
    pid_current_ch1_test.set_pid_limits_max(950)
    pid_current_ch1_test.over_regulation_percent = 0.5
    pid_current_ch1_test.mqtt_start()
    pid_current_ch1_test.start()

    pid_current_ch2_test = PIDControl(mqtt_topics_current_ch2_pid, mqtt_broker, mqtt_port, mqtt_user=None, mqtt_password=None, pid_max_range=65535, ki=10.2906382256080534, kd=0, kp=3.193398544311137)
    pid_current_ch2_test.set_pid_limits_min(0)
    pid_current_ch2_test.set_pid_limits_max(950)
    pid_current_ch2_test.over_regulation_percent = 0.5
    pid_current_ch2_test.mqtt_start()
    pid_current_ch2_test.start()

    sys_module = system_module.SystemModule(mqtt_broker, mqtt_port, 'abc', 'abc')

    try:
         while True:
              time.sleep(10)
    except KeyboardInterrupt:
        print('exiting')
        exit()


if __name__ == "__main__":
    main()
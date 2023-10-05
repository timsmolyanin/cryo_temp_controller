#!/root/wk/py310/bin/python

import pid_control
import nextion_mqtt_bridge
import paho.mqtt.client as mqtt
import random
import time
import queue
from loguru import logger

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

q = queue.Queue()


mqtt_topics_list = [("/devices/HeaterModule/controls/MEAS LDO REG Vout", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO Voltage RampRate", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO Voltage Setpoint", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO Voltage MAX", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO PID Kp", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO PID Ki", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO PID Kd", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO Current Setpoint", 0),
                           ("/devices/HeaterModuleSetpoints/controls/LDO Current MAX", 0),
                           ("/devices/HeaterModuleSetpoints/controls/Data Filter Type", 0),
                           ("/devices/HeaterModuleSetpoints/controls/Data Filter BufferSize", 0),
                           ("/devices/MeasureModuleSetpoints/controls/CH1 Current Setpoint", 0),
                           ("/devices/MeasureModuleSetpoints/controls/CH2 Current Setpoint", 0),
                           ("/devices/MeasureModuleSetpoints/controls/CH1 State", 0),
                           ("/devices/MeasureModuleSetpoints/controls/CH2 State", 0),
                           ("/devices/MeasureModule/controls/CH1 Current", 0),
                           ("/devices/MeasureModule/controls/CH2 Current", 0),
                           ("/devices/HeaterModule/controls/Output Voltage State", 0)
                           ]


def connect_mqtt(whois: str) -> mqtt:
    logger.debug(f"MQTT client in {whois} started connect to broker")
    client_id = f"dialtek-mqtt-{random.randint(0, 100)}"
    broker = "192.168.44.11"
    port = 1883
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.debug(f"{whois} Connected to MQTT Broker!")
        else:
            logger.debug(f"{whois} Failed to connect, return code {rc}")

    mqtt_client = mqtt.Client(client_id)
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(broker, port)
    return mqtt_client

def subscribe(client: mqtt):
    try:
        client.subscribe([("/devices/HeaterModule/controls/Output Voltage State", 0),
                          ("/devices/MeasureModuleSetpoints/controls/CH1 State", 0),
                          ("/devices/MeasureModuleSetpoints/controls/CH2 State", 0),
                        ])
        client.on_message = on_message
    except Exception as e:
        print(e)

def on_message(client, userdata, msg):
    topic_name = msg.topic.split("/")
    topic_val = msg.payload.decode("utf-8")

    q.put((topic_name[-1], int(topic_val)))


def mqtt_start():
    client = connect_mqtt(whois="Main function")
    subscribe(client)
    client.loop_start()


def main():
    logger.debug("Aplication is ran")
    mqtt_start()
    cc1_kp = 18.0
    cc1_ki = 4.6
    cc1_kd = 6.0
    ch1_k = 52.4813
    ch1_b = 35.3409
    ch1_limits = 3.5

    cc2_kp = 18.0
    cc2_ki = 4.6
    cc2_kd = 6.0
    ch2_k = 49.8919
    ch2_b = 24.6469
    ch2_limits = 3.5

    hv_kp = 100.0
    hv_ki = 14.6
    hv_kd = 6.0
    hv_k = 593.7
    hv_b = 522.13
    hv_limits = 20.5

    t1_kp = 4
    t1_ki = 0.3
    t1_kd = 0.0
    t1_k = 1
    t1_b = 1
    t1_limits = 1

    broker = "192.168.44.11"
    port = 1883
    comport = "COM5"
    baudrate = 115200

    ch1_current_mqtt_feedback_topic = "/devices/MeasureModule/controls/CH1 Current"
    ch1_current_mqtt_setpoint_topic = "/devices/MeasureModuleSetpoints/controls/CH1 Current Setpoint"
    ch1_current_mqtt_control_topic = "/devices/MeasureModule/controls/CH1 DAC/on"
    ch1_current_mqtt_output_topic = "/devices/FilteredValues/controls/CH1 Current"

    ch2_current_mqtt_feedback_topic = "/devices/MeasureModule/controls/CH2 Current"
    ch2_current_mqtt_setpoint_topic = "/devices/MeasureModuleSetpoints/controls/CH2 Current Setpoint"
    ch2_current_mqtt_control_topic = "/devices/MeasureModule/controls/CH2 DAC/on"
    ch2_current_mqtt_output_topic = "/devices/FilteredValues/controls/CH2 Current"

    heater_voltage_mqtt_feedback_topic = "/devices/HeaterModule/controls/MEAS LDO REG Vout"
    heater_voltage_mqtt_setpoint_topic = "/devices/HeaterModuleSetpoints/controls/LDO Voltage Setpoint"
    heater_voltage_mqtt_control_topic = "/devices/HeaterModule/controls/LDO Counts Set/on"
    heater_voltage_mqtt_output_topic = "/devices/FilteredValues/controls/LDO Voltage"

    ch1_temp_mqtt_feedback_topic = "/devices/FilteredValues/controls/CH1 Temperature"
    ch1_temp_mqtt_setpoint_topic = "/devices/MeasureModuleSetpoints/controls/CH1 Temperature Setpoint"
    ch1_temp_mqtt_control_topic = "/devices/HeaterModuleSetpoints/controls/LDO Voltage Setpoint/on"
    ch1_temp_mqtt_output_topic = "/devices/FilteredValues/controls/CH1 Temperature PID"

    ch1_current_pid = pid_control.PIDControl(broker, port, kp=cc1_kp, ki=cc1_ki, kd=cc1_kd, setpoint_topic=ch1_current_mqtt_setpoint_topic,
                            feedback_topic=ch1_current_mqtt_feedback_topic, control_topic=ch1_current_mqtt_control_topic,
                            output_value_topic=ch1_current_mqtt_output_topic, k=ch1_k, b=ch1_b, limits=ch1_limits,
                            mqtt_user=None, mqtt_passw=None)
    
    ch2_current_pid = pid_control.PIDControl(broker, port, kp=cc2_kp, ki=cc2_ki, kd=cc2_kd, setpoint_topic=ch2_current_mqtt_setpoint_topic,
                            feedback_topic=ch2_current_mqtt_feedback_topic, control_topic=ch2_current_mqtt_control_topic,
                            output_value_topic=ch2_current_mqtt_output_topic, k=ch2_k, b=ch2_b, limits=ch2_limits,
                            mqtt_user=None, mqtt_passw=None)
    
    heater_voltage_pid = pid_control.PIDControl(broker, port, kp=hv_kp, ki=hv_ki, kd=hv_kd, setpoint_topic=heater_voltage_mqtt_setpoint_topic,
                            feedback_topic=heater_voltage_mqtt_feedback_topic, control_topic=heater_voltage_mqtt_control_topic,
                            output_value_topic=heater_voltage_mqtt_output_topic, k=hv_k, b=hv_b, limits=t1_limits,
                            mqtt_user=None, mqtt_passw=None)
    
    ch1_temp_pid = pid_control.PIDControl(broker, port, kp=t1_kp, ki=t1_ki, kd=t1_kd, setpoint_topic=ch1_temp_mqtt_setpoint_topic,
                            feedback_topic=ch1_temp_mqtt_feedback_topic, control_topic=ch1_temp_mqtt_control_topic,
                            output_value_topic=ch1_temp_mqtt_output_topic, k=t1_k, b=t1_b, limits=hv_limits,
                            mqtt_user=None, mqtt_passw=None)

    nextion_mqtt_thread = nextion_mqtt_bridge.NextionMqttBridge(mqtt_port=port, mqtt_broker=broker, mqtt_passw=None, mqtt_user=None,
                                            comport_baudrate=baudrate, comport_name=comport)
    
    nextion_mqtt_thread.mqtt_start()
    nextion_mqtt_thread.start()

    ch1_current_pid.mqtt_start()
    ch1_current_pid.run_flag = True
    ch1_current_pid.name = "CH1 Current"
    ch1_current_pid.set_ramprate_func_available(False)
    ch1_current_pid.set_ramprate_func_en(False)
    ch1_current_pid.start()

    ch2_current_pid.mqtt_start()
    ch2_current_pid.run_flag = True
    ch2_current_pid.name = "CH2 Current"
    ch2_current_pid.set_ramprate_func_available(False)
    ch2_current_pid.set_ramprate_func_en(False)
    ch2_current_pid.start()

    heater_voltage_pid.mqtt_start()
    heater_voltage_pid.run_flag = True
    heater_voltage_pid.name = "Heater"
    heater_voltage_pid.set_ramprate_func_available(False)
    heater_voltage_pid.set_ramprate_func_en(False)
    heater_voltage_pid.start()

    ch1_temp_pid.mqtt_start()
    ch1_temp_pid.run_flag = True
    ch1_temp_pid.name = "Temperature 1"
    ch1_temp_pid.set_ramprate_func_available(False)
    ch1_temp_pid.set_ramprate_func_en(False)
    ch1_temp_pid.enable_calculate_pid_limits(False)
    ch1_temp_pid.set_pid_limits(0, 43)
    ch1_temp_pid.set_control_loop_period(1.0)
    ch1_temp_pid.start()
    

    while True:
        time.sleep(0.5)
        cmd = q.get()
        if cmd[0] == "CH1 State":
            ch1_current_pid.set_pid_automode_value(bool(cmd[1]))
            ch1_temp_pid.set_pid_automode_value(bool(cmd[1]))
        elif cmd[0] == "CH2 State":
            ch2_current_pid.set_pid_automode_value(bool(cmd[1]))
        elif cmd[0] == "Output Voltage State":
            heater_voltage_pid.set_control_value_state(bool(cmd[1]))
            heater_voltage_pid.set_ramprate_func_en(bool(cmd[1]))
       
        
if __name__ == "__main__":
    main()



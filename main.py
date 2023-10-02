#!/root/wk/py310/bin/python

import pid_control
import nextion_mqtt_bridge
import paho.mqtt.client as mqtt
import random
import time
import queue

import heater_voltage_ramp


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
                           ]


def connect_mqtt() -> mqtt:
    client_id = f"dialtek-mqtt-{random.randint(0, 100)}"
    broker = "192.168.44.11"
    port = 1883
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

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
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()


def main():
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

    hv_kp = 45.0
    hv_ki = 18.6
    hv_kd = 8.0
    hv_k = 585.8231
    hv_b = 471.0017
    hv_limits = 8.0

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
                            output_value_topic=heater_voltage_mqtt_output_topic, k=hv_k, b=hv_b, limits=hv_limits,
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
    # ch1_current_pid.set_mqtt_topics_list(mqtt_topics_list)
    ch1_current_pid.start()

    ch2_current_pid.mqtt_start()
    ch2_current_pid.run_flag = True
    ch2_current_pid.name = "CH2 Current"
    ch2_current_pid.set_ramprate_func_available(False)
    ch2_current_pid.set_ramprate_func_en(False)
    # ch2_current_pid.set_mqtt_topics_list(mqtt_topics_list)
    ch2_current_pid.start()

    heater_voltage_pid.mqtt_start()
    heater_voltage_pid.run_flag = True
    heater_voltage_pid.name = "Heater"
    heater_voltage_pid.set_ramprate_func_available(True)
    heater_voltage_pid.set_ramprate_func_en(False)
    # heater_voltage_pid.set_mqtt_topics_list(mqtt_topics_list)
    heater_voltage_pid.start()

    while True:
        time.sleep(0.5)
        cmd = q.get()
        if cmd[0] == "CH1 State":
            ch1_current_pid.set_pid_automode_value(bool(cmd[1]))
        elif cmd[0] == "CH2 State":
            ch2_current_pid.set_pid_automode_value(bool(cmd[1]))
        elif cmd[0] == "Output Voltage State":
            heater_voltage_pid.set_control_value_state(bool(cmd[1]))
            heater_voltage_pid.set_ramprate_func_en(bool(cmd[1]))
       
        
if __name__ == "__main__":
    main()

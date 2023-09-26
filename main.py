#!/root/wk/py310/bin/python

import serial_port
import mqtt_communication
import paho.mqtt.client as mqtt
from list_of_mqtt_topics import list_of_mqtt_topics
import time


def main():
    serial_com_port_name = "COM4"
    serial_com_port_speed = 115200
    mqtt_broker_address = "192.168.44.11"
    mqtt_broker_port = 1883

    sp = serial_port.serial_connect(serial_com_port_name, serial_com_port_speed)
    if sp[0]:
        client = mqtt.Client()
        mqtt_subscribe_topics = list_of_mqtt_topics

        mqtt_test = mqtt_communication.MQTTSubscriberThread(client, mqtt_broker_address, mqtt_broker_port, mqtt_subscribe_topics, sp[1])
        mqtt_test.start()

        nex_reader = serial_port.NextionReader(sp[0], sp[1])
        nex_reader.start()
        
        # cmd1 = "welcome.q0.picc=47"
        # cmd2 = "welcome.q1.picc=49"
        # cmd3 = "welcome.progress.en=0"
        # serial_port.serial_write(sp[1], cmd1)
        # serial_port.serial_write(sp[1], cmd2)
        # serial_port.serial_write(sp[1], cmd3)
        # time.sleep(2)
        # cmd4 = "page 0"
        # serial_port.serial_write(sp[1], cmd4)

        # cmd4 = "page 4"
        # serial_port.serial_write(sp[1], cmd4)
        # cmd5 = "welcome.progress.en=1"
        # serial_port.serial_write(sp[1], cmd5)
        # cmd6 = "welcome.q1.picc=48"
        # serial_port.serial_write(sp[1], cmd6)

if __name__ == "__main__":
    main()

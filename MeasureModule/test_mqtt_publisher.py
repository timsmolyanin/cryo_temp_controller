from threading import Thread
from paho.mqtt.client import Client as mqtt_client
from paho.mqtt.client import MQTTMessage
from paho.mqtt import publish
from loguru import logger
import sys
import random
from time import sleep
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class Test_MQTTPublisher(Thread):
    def __init__(self, broker, channel_number : int, port = 1883, username=None, password=None):
        super().__init__()

        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = f'publish-{random.randint(0, 100)}'
        self.channel_number = channel_number

        self.topic_path = "/devices/MeasureModule/controls"
        

    def run(self):
        self.client = self.connect_mqtt("MQTT Publisher Test")
        self.client.loop_start()
        self.publish()
        self.client.loop_stop()

    def connect_mqtt(self, whois : str) -> mqtt_client: 

        def on_connect(client, userdata, flags, rc):
            print(f"Connected with result code {rc}")
            if rc == 0:
                logger.debug(f"{whois} Connected to MQTT Broker!")
            else:
                logger.debug(f"{whois} Failed to connect, return code {rc}")
                 
        client = mqtt_client(self.client_id)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client
    
    def publish(self):

        i_CH1 = 2
        i_CH2 = 1

        self.topics = [
            (f"{self.topic_path}/CH{i_CH1} SensorModel", 'Diode'),
            (f"{self.topic_path}/CH{i_CH1} ConfigFname", 'CDA005.340'),
            (f"{self.topic_path}/CH{i_CH1} FilterType", 'Median'),
            (f"{self.topic_path}/CH{i_CH1} FilterBufferSize", 10),
            (f"{self.topic_path}/CH{i_CH2} SensorModel", 'Pt1000'),
            (f"{self.topic_path}/CH{i_CH2} ConfigFname", 'pt1000_config_2.txt'),
            (f"{self.topic_path}/CH{i_CH2} FilterType", 'Median'),
            (f"{self.topic_path}/CH{i_CH2} FilterBufferSize", 10),
        ]
        for i in self.topics:
            self.client.publish(i[0], i[1], retain=True, qos=2)

        # while True:
        #     sleep(1)
        #     voltage = 1010 + (random.random() * 20 - 10)
        #     resistance = 300 + (random.random() * 100 - 50)

        #     topics = [
        #         (f"{self.topic_path}/CH{1} Voltage", voltage),
        #         (f"{self.topic_path}/CH{1} Resistance", resistance),
        #         (f"{self.topic_path}/CH{2} Voltage", voltage),
        #         (f"{self.topic_path}/CH{2} Resistance", resistance)
        #     ]

        #     for i in topics:
        #         self.client.publish(i[0], i[1])


def test():
    broker = "192.168.0.104"
    # broker = "127.0.0.1"

    port = 1883

    mqtt_sensor = Test_MQTTPublisher(broker=broker, port=port, channel_number=1)
    mqtt_sensor.start()

if __name__ == "__main__":
    test()



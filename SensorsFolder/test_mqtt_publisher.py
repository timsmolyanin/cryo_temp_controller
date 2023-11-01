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

        self.topic_path = "/devices/MeasureModule"
        

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

        for i in range(4):
            self.topics = [
                (f"{self.topic_path}/CH{i+1}/SensorModel", 0),
                (f"{self.topic_path}/CH{i+1}/ConfigFname", 0),
                (f"{self.topic_path}/CH{i+1}/FilterType", 0),
                (f"{self.topic_path}/CH{i+1}/FilterBufferSize", 0),
                (f"{self.topic_path}/CH{i+1}/Voltage", 0),
                (f"{self.topic_path}/CH{i+1}/Resistance", 0),
                (f"{self.topic_path}/CH{i+1}/Temperature", 0),
                (f"{self.topic_path}/CH{i+1}/SetCurrent", 0),
                (f"{self.topic_path}/CH{i+1}/State", 0)
            ]
            for i in self.topics:
                self.client.publish(i[0], i[1])

        while True:
            sleep(1)
            voltage = 1.01 + (random.random() * 0.02 - 0.01)
            resistance = 1000 + (random.random() * 50 - 25)
            for i in range(4):
                topics = [
                    (f"{self.topic_path}/CH{i+1}/Voltage", voltage),
                    (f"{self.topic_path}/CH{i+1}/Resistance", resistance)
                ]

                for i in topics:
                    self.client.publish(i[0], i[1])

def test():
    broker = "127.0.0.1"
    port = 1883

    mqtt_sensor = Test_MQTTPublisher(broker=broker, port=port, channel_number=1)
    mqtt_sensor.start()

if __name__ == "__main__":
    test()



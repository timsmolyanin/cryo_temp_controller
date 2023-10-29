from threading import Thread
from paho.mqtt import client as mqtt_client
from paho.mqtt import *
import random
from Sensors import *
from loguru import logger
import sys
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class MQTTSensor(Thread):
    def __init__(self, broker, port = 1883, username=None, password=None):
        super().__init__()

        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = f'MQTT_sensor-{random.randint(0, 100)}'

        self.topic = [
            ("/devices/MeasureModule/controls/CH1 Voltage", 0),
            ("/devices/MeasureModule/controls/CH1/SwichSensor/Diode", 0), # Topic for changing the sensor to diode
            ("/devices/MeasureModule/controls/CH1/SwichSensor/Pt1000", 0) # topic for changing the sensor to Pt1000
        ]

        self.sensor = PtSensor("SensorsFolder\Sensors\ConfigFolder\pt1000_config.txt")

    def run(self):
        client = self.connect_mqtt("MQTT Sensor")
        self.subscribe(client)
        client.loop_forever()

    def connect_mqtt(self, whois : str) -> mqtt_client: 

        def on_connect(client, userdata, flags, rc):
            print(f"Connected with result code {rc}")
            if rc == 0:
                logger.debug(f"{whois} Connected to MQTT Broker!")
            else:
                logger.debug(f"{whois} Failed to connect, return code {rc}")
                 
        client = mqtt_client.Client(self.client_id)
        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def on_message(self, client : mqtt_client, userdata, msg):
        print(f"Message received [{msg.topic}]: {msg.payload.decode()}")
        topic = msg.topic.split("/")
        playload = float(msg.payload.decode())
        match topic[4]:
            case "CH1 Voltage":
                client.publish("/devices/FilteredValues/controls/CH1 Temperature", self.sensor.convert(playload))
            case "CH1":
                match topic[-1]:
                    case "Diode":
                        self.sensor = DiodeSensor("SensorsFolder\Sensors\ConfigFolder\diodChine.txt")
                    case "Pt1000":
                        self.sensor = PtSensor("SensorsFolder\Sensors\ConfigFolder\pt1000_config.txt")


    def subscribe(self, client: mqtt_client):
        try:
            client.subscribe(self.topic) 
            client.on_message = self.on_message
        except Exception as e:
            print(e)

def test():
    broker = "127.0.0.1"
    port = 1883

    mqtt_sensor = MQTTSensor(broker=broker, port=port)
    mqtt_sensor.start()

if __name__ == "__main__":
    test()
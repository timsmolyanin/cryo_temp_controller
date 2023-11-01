from threading import Thread
from paho.mqtt.client import Client as mqtt_client
from paho.mqtt.client import MQTTMessage
from paho.mqtt import publish
from Sensors import *
from Filters import *
from loguru import logger
import sys
import random
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class MQTTSensor(Thread):
    def __init__(self, broker, channel_number : int, port = 1883, username=None, password=None, buffer_size=10):
        super().__init__()

        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = f'MQTT_sensor-{random.randint(0, 100)}'
        self.channel_number = channel_number

        self.buffer_size = buffer_size

        self.config_file_path = "SensorsFolder/Sensors/ConfigFolder"

        self.topic_path = "/devices/MeasureModule/controls"
        self.topics = [
            (f"{self.topic_path}/CH{self.channel_number}/SensorModel", 0),
            (f"{self.topic_path}/CH{self.channel_number}/ConfigFname", 0),
            (f"{self.topic_path}/CH{self.channel_number}/FilterType", 0),
            (f"{self.topic_path}/CH{self.channel_number}/FilterBufferSize", 0),
            (f"{self.topic_path}/CH{self.channel_number}/Voltage", 0),
            (f"{self.topic_path}/CH{self.channel_number}/Resistance", 0)
        ]

        self.sensor = None
        self.filterType = None

    def run(self):
        self.client = self.connect_mqtt("MQTT Sensor")
        self.subscribe()
        self.client.loop_forever()

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

    def on_message(self, client : mqtt_client, userdata, msg : MQTTMessage):
        print(f"Message received [{msg.topic}]: {msg.payload.decode()}")
        topic = msg.topic.split("/")[1:]
        playload = msg.payload.decode()
        f_playload = None
        try:
            f_playload = float(playload)
        except Exception as e:
            self.publish_error(str(e))
        
        if self.topic_path == f"/{topic[0]}/{topic[1]}/{topic[2]}":
            if topic[3] == f"CH{self.channel_number}":
                match topic[4]:
                    case "SensorModel":
                        print("Switch Sensor")
                        match playload:
                            case "Diode":
                                self.sensor = DiodeSensor(id=100)
                            case "Pt1000":
                                self.sensor = PtSensor(id=45)
                            case "Pt100":
                                self.sensor = PtSensor(id=40)
                            # case "TVO":
                            #     pass
                        if self.sensor != None:
                            client.publish(topic=f"{self.topic_path}/CH{self.channel_number}/SetCurrent", payload=self.sensor.id)
                            self.sensor.event_error = self.publish_error

                            if self.filterType != None:
                                self.filterType.clear()
                            else:
                                self.publish_error("FilterType = None")
                        else:
                            self.publish_error("Sensor = None")

                    case "ConfigFname":
                        print("Config")
                        try:
                            self.sensor.load_config(f"{self.config_file_path}/{playload}")
                        except Exception as e:
                            self.publish_error(str(e))

                    case "FilterType":
                        print("Switch Filter", end=" ")
                        match playload:
                            case "Median":
                                self.filterType = Median(self.buffer_size)
                                print("Median", end=" ")
                            case "FloatWindow":
                                self.filterType = MovingAverage(self.buffer_size)
                                print("FloatWindow", end=" ")
                        print()

                    case "FilterBufferSize":
                        print("Change Buffer", playload)
                        if f_playload == None:
                            self.publish_error("Playload is not float")
                            return
                        if self.filterType == None:
                            self.publish_error("FilterType = None")
                            return
                        
                        self.filterType.change_buffer(int(f_playload))

                    case "Voltage":
                        print("Voltage", playload)
                        if self.sensor == None:
                            self.publish_error("Sensor = None")
                            return
                        if f_playload == None:
                            self.publish_error("Playload is not float")
                            return
                        
                        if self.sensor.type == SensorType.VOLTAGE:
                            self.convert(f_playload)

                    case "Resistance":
                        print("Resistance", playload)
                        if self.sensor == None:
                            self.publish_error("Sensor = None")
                            return
                        if f_playload == None:
                            self.publish_error("Playload is not float")
                            return
                        
                        if self.sensor.type == SensorType.RESISTANCE:
                            self.convert(f_playload)



    def subscribe(self):
        try:
            self.client.subscribe(self.topics) 
            self.client.on_message = self.on_message
        except Exception as e:
            self.publish_error(str(e))
    
    def convert(self, playload : float):
        try:
            self.filterType.add_value(float(playload))
            self.client.publish(topic=f"{self.topic_path}/CH{self.channel_number}/Temperature", payload=self.sensor.convert(self.filterType.filtering()))
        except Exception as e:
            self.publish_error(str(e))
            

    def publish_error(self, massage):
        self.client.publish(topic=f"{self.topic_path}/CH{self.channel_number}/State", payload=str(massage))
        logger.error(massage)

def test():
    broker = "127.0.0.1"
    port = 1883

    topics = [
            (f"/devices/MeasureModule/controls/CH1/SensorModel", 0),
            (f"/devices/MeasureModule/controls/CH1/ConfigFname", 0),
            (f"/devices/MeasureModule/controls/CH1/FilterType", 0),
            (f"/devices/MeasureModule/controls/CH1/FilterBufferSize", 0),
            (f"/devices/MeasureModule/controls/CH1/Voltage", 0),
            (f"/devices/MeasureModule/controls/CH1/Resistance", 0),
            (f"/devices/MeasureModule/controls/CH1/Temperature", 0),
            (f"/devices/MeasureModule/controls/CH1/SetCurrent", 0),
            (f"/devices/MeasureModule/controls/CH1/State", 0)
        ]

    publish.multiple(topics, hostname=broker, port=port)

    mqtt_sensor = MQTTSensor(broker=broker, port=port, channel_number=1)
    mqtt_sensor.start()

    topics = [
            (f"/devices/MeasureModule/controls/CH1/SensorModel", "Pt1000"),
            (f"/devices/MeasureModule/controls/CH1/ConfigFname", "pt1000_config.txt"),
            (f"/devices/MeasureModule/controls/CH1/FilterType", "Median"),
            (f"/devices/MeasureModule/controls/CH1/FilterBufferSize", 5)
        ]
    publish.multiple(topics, hostname=broker, port=port)

if __name__ == "__main__":
    test()
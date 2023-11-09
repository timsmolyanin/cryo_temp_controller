from threading import Thread
from paho.mqtt.client import Client as mqtt_client
from paho.mqtt.client import MQTTMessage
from paho.mqtt import publish
from Sensors import *
from Filters import *
from loguru import logger
import sys
import random
from pathlib import Path
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

        # self.config_file_path = "~/measure_module/Sensors"
        self.config_file_path = Path(__file__).parent.joinpath('Sensors').joinpath('ConfigFolder')

        self.topic_path = "/devices/MeasureModule/controls"
        self.out_topic_path = '/devices/FilteredValues/controls'
        self.topics = [
            (f"{self.topic_path}/CH{self.channel_number} SensorModel", 0),
            (f"{self.topic_path}/CH{self.channel_number} ConfigFname", 0),
            (f"{self.topic_path}/CH{self.channel_number} FilterType", 0),
            (f"{self.topic_path}/CH{self.channel_number} FilterBufferSize", 0),
            (f"{self.topic_path}/CH{self.channel_number} Voltage", 0),
            (f"{self.topic_path}/CH{self.channel_number} Resistance", 0)
        ]

        self.sensor = None
        self.filterType = None

    def run(self):
        self.client = self.connect_mqtt(f"MQTT Sensor CH{self.channel_number}")
        self.subscribe()
        self.client.loop_forever()

    def connect_mqtt(self, whois : str) -> mqtt_client: 

        def on_connect(client, userdata, flags, rc):
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
        # print(f"Message received [{msg.topic}]: {msg.payload.decode()}")
        topic = msg.topic.split("/")[1:]
        playload = msg.payload.decode()
        # if msg.topic.startswith(f"{self.topic_path}/CH {self.channel_number}"): 
        match topic[-1].split(' ')[-1]:
            case "SensorModel":
                logger.trace("Switch Sensor")
                match playload:
                    case "Diode":
                        self.sensor = DiodeSensor(current=100)
                    case "Pt1000":
                        self.sensor = PtSensor(current=45)
                    case "Pt100":
                        self.sensor = PtSensor(current=40)
                    case _: # мы не знаем такого типа датчика
                        self.publish_state(ValueError(f'Could not resolve sensor type `{playload}`. Current sensor type: {self.sensor.name}'))
                        return
                     
                self.publish_state("Ok")
                client.publish(topic=f"{self.topic_path}/CH{self.channel_number} SetCurrent", payload=self.sensor.current)
                self.sensor.event_error = self.publish_state
                self.sensor.name = playload

                if self.filterType == None:
                    self.publish_state("FilterType = None")
                    return
                
                self.filterType.clear()

            case "ConfigFname":
                try:
                    self.sensor.load_config(self.config_file_path.joinpath(playload))
                    self.publish_state("Ok")
                except Exception as e:
                    self.publish_state(e)
                    return
                

            case "FilterType":
                logger.trace("Switch Filter " + playload)
                match playload:
                    case "Median":
                        self.filterType = Median(self.buffer_size)
                    case "MovingAverage":
                        self.filterType = MovingAverage(self.buffer_size)
                    case _:
                        raise ValueError(f'Could not resolve filter type {playload}')
                    
                self.publish_state("Ok")

            case "FilterBufferSize":
                logger.trace("Change Buffer", playload)
                try:
                    f_playload = float(playload)
                except Exception as e:
                    self.publish_state(str(e))
                    return
                
                if self.filterType == None:
                    self.publish_state("FilterType = None")
                    return
                
                self.filterType.change_buffer(int(f_playload))
                self.publish_state("Ok")

            case "Voltage":
                try:
                    f_playload = float(playload)
                except Exception as e:
                    self.publish_state(str(e))
                    return

                if self.sensor == None:
                    self.publish_state("Sensor = None")
                    return
                
                if self.sensor.type == SensorType.VOLTAGE:
                    self.convert(f_playload)

            case "Resistance":
                try:
                    f_playload = float(playload)
                except Exception as e:
                    self.publish_state(str(e))
                    return

                if self.sensor == None:
                    self.publish_state("Sensor = None")
                    return
                
                if self.sensor.type == SensorType.RESISTANCE:
                    self.convert(f_playload)



    def subscribe(self):
        try:
            self.client.subscribe(self.topics) 
            self.client.on_message = self.on_message
        except Exception as e:
            self.publish_state(e)
    
    def convert(self, playload : float):
        try:
            self.filterType.add_value(float(playload))
            self.client.publish(topic=f"{self.out_topic_path}/CH{self.channel_number} Temperature", payload=self.sensor.convert(self.filterType.filtering()))
        except Exception as e:
            self.publish_state(str(e))
            

    def publish_state(self, massage):
        self.client.publish(topic=f"{self.out_topic_path}/CH{self.channel_number} State", payload=str(massage))
        if str(massage) == "Ok":
            logger.debug(massage)
        else:
            logger.error(massage)

def test():
    # broker = "192.168.0.104"
    broker = "127.0.0.1"
    port = 1883

    mqtt_sensor1 = MQTTSensor(broker=broker, port=port, channel_number=1)
    mqtt_sensor1.start()

    mqtt_sensor2 = MQTTSensor(broker=broker, port=port, channel_number=2)
    mqtt_sensor2.start()



if __name__ == "__main__":
    test()

from paho.mqtt.client import Client as mqtt_client
from paho.mqtt.client import MQTTMessage
from paho.mqtt import publish
from Sensors import *
from Filters import *
from loguru import logger
import sys
import random
from pathlib import Path
from time import sleep, time
from threading import Thread
logger.remove()
logger.add(sys.stdout, level="DEBUG")

class MeasureModule():

    value_timeout = 10 # seconds

    def __init__(self, broker, channel_number : int, port = 1883, username=None, password=None, buffer_size=10):
        try:
            self.broker = broker
            self.port = port
            self.username = username
            self.password = password
            self.client_id = f'MQTT_sensor-{random.randint(0, 100)}'
            self.channel_number = channel_number
            self.buffer_size = buffer_size
            self.config_file_path = Path(__file__).parent.joinpath('Sensors').joinpath('ConfigFolder')
            self.topic_path = "/devices/MeasureModule/controls"
            self.out_topic_path = '/devices/FilteredValues/controls'
            self.topics = [
                (f"{self.topic_path}/CH{self.channel_number} FilterType", 0),
                (f"{self.topic_path}/CH{self.channel_number} SensorModel", 0),
                (f"{self.topic_path}/CH{self.channel_number} ConfigFname", 0),
                (f"{self.topic_path}/CH{self.channel_number} FilterBufferSize", 0),
                # (f"{self.topic_path}/CH{self.channel_number} Voltage", 0),
                # (f"{self.topic_path}/CH{self.channel_number} Resistance", 0)
            ]
            self.sensor = None
            self.value_filter = None
            self.state = 'INIT'
            self.last_value_update_time = time()
            self.is_connected = False
            self.timeout_thread = None
        except Exception as err:
            self.publish_state(err)


    def start(self):
        self.connect_mqtt(f"MQTT Sensor CH{self.channel_number}")
        self.subscribe()
        self.client.loop_start() # starts a separate thread (created by paho library)
        self.timeout_thread = Thread(target=self.check_timeout, daemon=True)
        self.timeout_thread.start()


    def check_timeout(self):
        while True:
            sleep(10)
            if not self.is_connected or self.state !='OK':
                continue
            if time() - self.last_value_update_time >10: # check last refresh time
                self.publish_state(TimeoutError(f'Temperature has not been refreshed for more than 10 seconds.'))

    
    def connect_mqtt(self, whois : str):        
        self.client = mqtt_client(self.client_id)
        # client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect(self.broker, self.port)


    def on_connect(self, client, userdata, flags, rc):
            if rc == 0:
                logger.debug(f"CH{self.channel_number}: Connected to MQTT Broker!")
                self.is_connected = True
                self.publish_state('OK')
            else:
                self.publish_state(f'Could not connect to MQTT broker, return code {rc}')


    def on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        self.publish_state(ConnectionError('Lost connection to mqtt broker, attempting to reconnect'))


    def on_message(self, client : mqtt_client, userdata, msg : MQTTMessage):
        try:
            topic = msg.topic.split("/")[1:]
            playload = msg.payload.decode()
            match topic[-1].split(' ')[-1]:

                case "SensorModel":
                    client.unsubscribe(f"{self.topic_path}/CH{self.channel_number} Voltage")
                    client.unsubscribe(f"{self.topic_path}/CH{self.channel_number} Resistance")
                    match playload:
                        case "Diode":
                            self.sensor = DiodeSensor(current=100)
                        case "Pt1000":
                            self.sensor = PtSensor(current=45)
                        case "Pt100":
                            self.sensor = PtSensor(current=40)
                        case _: # мы не знаем такой тип датчика
                            raise ValueError(f'Could not resolve sensor type `{playload}`. Current sensor type: {self.sensor.name}')
                    
                    match self.sensor.type:
                        case SensorType.VOLTAGE:
                            client.subscribe(f"{self.topic_path}/CH{self.channel_number} Voltage", 0)
                        case SensorType.RESISTANCE:
                            client.subscribe(f"{self.topic_path}/CH{self.channel_number} Resistance", 0)
                        case _:
                            raise ValueError(f'SensorType error')
                        
                    logger.debug(f"CH{self.channel_number}: SensorModel changed to {playload}")
                    client.publish(topic=f"{self.topic_path}/CH{self.channel_number} SetCurrent", payload=self.sensor.current)
                    self.sensor.name = playload
                    if self.value_filter == None:
                        raise AttributeError("Value filter is not initialized")               
                    self.value_filter.clear()

                case "ConfigFname":
                    logger.debug(f"CH{self.channel_number}: ConfigFname changed to {playload}")
                    self.sensor.load_config(self.config_file_path.joinpath(playload))
                    # self.publish_state("OK")
                    
                case "FilterType":
                    logger.debug(f"CH{self.channel_number}: Filter type changed to {playload}")
                    match playload:
                        case "Median":
                            self.value_filter = Median(self.buffer_size)
                        case "MovingAverage":
                            self.value_filter = MovingAverage(self.buffer_size)
                        case _:
                            raise ValueError(f'Could not resolve filter type {playload}')

                case "FilterBufferSize":
                    if self.value_filter == None:
                        raise AttributeError("Value filter is not initialized")
                    logger.debug(f'CH{self.channel_number}: Filter buffer size changed to {playload}')
                    f_playload = float(playload)                    
                    self.value_filter.change_buffer_size(int(f_playload))

                case "Voltage":
                    f_playload = float(playload)
                    if self.sensor == None:
                        raise AttributeError("Sensor = None")
                    if self.sensor.type != SensorType.VOLTAGE:
                        raise TypeError('Incorrect sensor type')
                    self.convert(f_playload)

                case "Resistance":
                    f_playload = float(playload)
                    if self.sensor == None:
                        raise AttributeError("Sensor = None")
                    if self.sensor.type != SensorType.RESISTANCE:
                        raise TypeError('Incorrect sensor type')
                    self.convert(f_playload)

            self.publish_state("OK")
        except Exception as err:
            self.publish_state(err)     


    def subscribe(self):
        try:
            self.client.subscribe(self.topics) 
            self.client.on_message = self.on_message
        except Exception as e:
            self.publish_state(e)
    

    def convert(self, playload : float):
        filtered_value = self.value_filter.filter_value(float(playload))
        self.client.publish(topic=f"{self.out_topic_path}/CH{self.channel_number} Temperature", payload=self.sensor.convert(filtered_value))
        self.last_value_update_time = time()


    def publish_state(self, massage):
        if massage is self.state: # to avoid publishing same message multiple times
            return
        out_str = massage
        self.state = massage
        if isinstance(massage, Exception): 
            out_str = f'{massage.__class__.__name__}: {out_str}' # adding exception type to message
            logger.error(f'CH{self.channel_number}: {out_str}')
        else:
            logger.debug(f'CH{self.channel_number}: {out_str}')
        self.client.publish(topic=f"{self.out_topic_path}/CH{self.channel_number} State", payload=out_str)
            


def create_modules():
    #TODO: read config with cryo_control channel configuration
    broker = "127.0.0.1"
    port = 1883

    ch1_module = MeasureModule(broker=broker, port=port, channel_number=1)
    ch1_module.start()

    ch2_module = MeasureModule(broker=broker, port=port, channel_number=2)
    ch2_module.start()



if __name__ == "__main__":
    create_modules()
    try:
        while True:
            sleep(100)
    except KeyboardInterrupt:
        print('exiting')
        exit()

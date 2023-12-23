from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
from loguru import logger

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


class Mqtt(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_password:str, module_name:str, on_message_config:dict, topic_list:dict, parent=None):
        super(Mqtt, self).__init__(parent)
        
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.client_id = f"dialtek-mqtt-{random.randint(0, 100)}"
        
        self.name = module_name
        self.topic_list = topic_list
        self.on_message_config = on_message_config
        
    


    def connect_mqtt(self, whois: str) -> mqtt:
        logger.debug(f"MQTT client in {whois} started connect to broker")
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.debug(f"{whois} Connected to MQTT Broker!")
                return
            else:
                logger.debug(f"{whois} Failed to connect, return code {rc}")

        mqtt_client = mqtt.Client(self.client_id)
        mqtt_client.on_connect = on_connect
        mqtt_client.connect(self.broker, self.port)
        return mqtt_client
    
    def unsubscribe(self, client: mqtt):
        for key, value in self.topic_list.items():
            if not "output" in key:
                client.unsubscribe(value)
    

    def subscribe(self, client: mqtt):
        for key, value in self.topic_list.items():
            if not "output" in key:
                client.subscribe(value)
        client.on_message = self.on_message
        
    def change_topic(self, topic_to_change, topic):
        self.unsubscribe(self.client)
        self.topic_list[topic_to_change[13:]] = topic
        self.subscribe(self.client)
    
    def get_key_by_value(self, value):
        for key, v in self.topic_list.items():
            if v == value:
                return key
    
    def on_message(self, client, userdata, msg):
        topic_name = msg.topic 
        topic_value = msg.payload.decode("utf-8")
        
        if ("change_topic" in self.get_key_by_value(topic_name)):
            self.change_topic(self.get_key_by_value(topic_name), topic_value)
        else:
            try:
                self.on_message_config[topic_name](topic_value)
            except:
                logger.debug(f"{self.name}: Ошибка в распознавании топика")
                     
    def start(self):
        self.client = self.connect_mqtt(self.name)
        self.subscribe(self.client)
        self.client.loop_start()

    #Публикует топик с именем topic_name и значением topic_value
    def publish_topic(self, topic_name: str, topic_value):
        publish.single(str(topic_name), str(topic_value), hostname=self.broker)
    
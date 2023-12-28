from threading import Thread
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import mqtt_module
from loguru import logger
import time
import random


from list_of_mqtt_topics import mqtt_topics_plotter_module

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


class TestClass(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_password:str, parent=None):
        
        super(TestClass, self).__init__(parent)
        self.name = "test_module"
        self.topic_list = {
                "input_temperature1": "/devices/MeasureModuleOutputs/controls/CH1 MeasureModule Temperature",
                "input_temperature2": "/devices/MeasureModuleOutputs/controls/CH2 MeasureModule Temperature"
        }

        self.on_message_config = {
            self.topic_list["input_temperature1"] : self.set_temperature1,
            self.topic_list["input_temperature2"] : self.set_temperature2,
        }
        
        self.mqtt = mqtt_module.Mqtt(mqtt_broker, mqtt_port, mqtt_user, mqtt_password, self.name, self.on_message_config, self.topic_list)
        self.mqtt.start()
    
    def run(self):
        val1 = 75
        val2 = 150
        while True:
            if random.randint(1,2) == 1:
                self.mqtt.publish_topic(self.topic_list["input_temperature1"], str(val1 + random.randint(0,10)))
                
            if random.randint(1,2) == 1:
                self.mqtt.publish_topic(self.topic_list["input_temperature2"], str(val2 + random.randint(0,10)))
            time.sleep(0.25)


    def set_temperature1(self, val):
        pass
    def set_temperature2(self, val):
        pass
    
def test():
    broker = "127.0.0.1"
    # broker = "192.168.44.11"
    port = 1883
    test = TestClass(broker, port, 'abc', 'abc')
    test.run()


if __name__ == "__main__":
    test()
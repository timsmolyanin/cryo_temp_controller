from threading import Thread
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import mqtt_module
import os
import nmcli
from loguru import logger
import time
import ipaddress


from list_of_mqtt_topics import mqtt_topics_plotter_module

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


class PlotterModule(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_password:str, parent=None):
        
        super(PlotterModule, self).__init__(parent)
        self.name = "plotter_module"
        self.topic_list = mqtt_topics_plotter_module

        self.on_message_config = {
            self.topic_list["input_user_scale_min"] : self.set_user_plot_min,
            self.topic_list["input_user_scale_max"] : self.set_user_plot_max,
            self.topic_list["input_temperature1"] : self.set_temperature1,
            self.topic_list["input_temperature2"] : self.set_temperature2,
            self.topic_list["input_update_scaling"] : self.update_scaling,
        }
        
        self.mqtt = mqtt_module.Mqtt(mqtt_broker, mqtt_port, mqtt_user, mqtt_password, self.name, self.on_message_config, self.topic_list)
        self.mqtt.start()
        

        self.user_plot_min = 75
        self.user_plot_max = 330

        self.buffer_temp_1 = []
        self.buffer_temp_2 = []
        self.buffer_size = 100

        self.publish_delay = 1


    def update_scaling(self):
        self.publish_delay = 0.05
        for i in range(self.buffer_size):

            self.publish_temperature("output_rescaled_temp1", self.buffer_temp_1[i])
            self.publish_temperature("output_rescaled_temp2", self.buffer_temp_2[i])

        self.publish_delay = 1


    def set_temperature1(self, value):
        temp1 = float(value)

        self.buffer_temp_1.append(temp1)
        if (self.buffer_temp_1.count() >= self.buffer_size):
            self.buffer_temp_1.pop(0)

        self.publish_temperature("output_rescaled_temp1", temp1)

    def set_temperature2(self, value):
        temp2 = float(value)

        self.buffer_temp_2.append(temp2)
        if (self.buffer_temp_2.count() >= self.buffer_size):
            self.buffer_temp_2.pop(0)

        self.publish_temperature("output_rescaled_temp2", temp2)



    def publish_temperature(self, name, temp):
        rescaled_temp = self.waveform_scaling(temp)
        self.mqtt.publish_topic(self.topic_list[name], rescaled_temp)


    def waveform_scaling(self, value: float):
        nextion_min, nextion_max = 0, 255
        user_range = self.user_plot_max - self.user_plot_min  
        nextion_range = nextion_max - nextion_min  
        converted = int(((value - self.user_plot_min) * nextion_range / user_range) + nextion_min)
        return converted
    
    def set_user_plot_min(self, value):
        self.user_plot_min = int(value)

    
    def set_user_plot_max(self, value):
        self.user_plot_max = int(value)
        
    
def test():
    broker = "127.0.0.1"
    # broker = "192.168.44.11"
    port = 1883
    test = PlotterModule(broker, port, 'abc', 'abc')
    while True:
        time.sleep(test.publish_delay)


if __name__ == "__main__":
    test()
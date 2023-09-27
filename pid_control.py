

from simple_pid import PID
from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time
import statistics


class PIDControl(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_passw:str,
                  kp:float, ki:float, kd:float, setpoint_topic:str, feedback_topic:str, control_topic:str,  parent=None):
        super(PIDControl, self).__init__(parent)
        self.run_flag = False
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.client_id = f'python-mqtt-{random.randint(0, 100)}'
        self.mqtt_setpoint_topic = setpoint_topic
        self.mqtt_feedback_topic = feedback_topic
        self.mqtt_control_topic = control_topic
        self.mqtt_output_topic = "/devices/FilteredValues/controls/CH2 Current"
        self.feedback_value = 0.0
        self.setpoint_value = 0.0
        self.buffer_size = 60
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.mov_av_list = list()
        self.median_list = list()
        self.filter_selector = 1
        self.pid = PID(self.kp, self.ki, self.kd, setpoint=self.setpoint_value)


    def run(self):
        while self.run_flag:
            time.sleep(0.05)
            calc_counts = self.calc_current_counts(self.setpoint_value)
            min = calc_counts - self.calc_proc(calc_counts, 2.5)
            max = calc_counts + self.calc_proc(calc_counts, 2.5)
            self.pid.setpoint = self.setpoint_value
            self.pid.output_limits = (min, max)
            control = self.pid(self.feedback_value)
            self.update(int(control))
        
            match self.filter_selector:
                case 0:
                    self.set_mqtt_topic_value(self.mqtt_output_topic, self.feedback_value)
                case 1:
                    # calculate moving average
                    self.calculate_moving_average(self.buffer_size, self.feedback_value)
                    self.calculate_median(self.buffer_size, self.feedback_value)
                case 2:
                    # calculate median
                    self.calculate_median(self.buffer_size, self.feedback_value)

    
    def stop_thread(self):
        self.run_flag = False
        self.join()
    
    def calc_current_counts(self, x):
        x = float(x)
        y = 49.8919 * x + 24.6469
        return int(y)


    def calc_proc(self, val, proc):
        value = (val * proc) / 100
        return int(value)
    
    def mqtt_set_setpoint(self, setpoint: str):
        if isinstance(setpoint, str):
            if setpoint == "":
                self.setpoint_value = 0.0
            else:
                self.setpoint_value = float(setpoint)
        else:
            raise TypeError(f"Type for setpoint must be str, not {type(setpoint)}!")
    
    def mqtt_set_feedback(self, feedback: str):
        if isinstance(feedback, str):
            if feedback == "":
                self.feedback_value = 0.0
            else:
                self.feedback_value = float(feedback)
        else:
            raise TypeError(f"Type for feedback must be str, not {type(feedback)}!")
    
    def set_run_flag(self, state: bool):
        if isinstance(state, bool):
            self.run_flag = state
        else:
            raise TypeError(f"Type for state must be bool, not {type(state)}!")

    def set_buffer_size(self, buffer_size: int):
        if isinstance(buffer_size, int):
            self.buffer_size = buffer_size
        else:
            raise TypeError(f"Type for buffer_size must be integer, not {type(buffer_size)}!")

    def connect_mqtt(self) -> mqtt:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        mqtt_client = mqtt.Client(self.client_id)
        mqtt_client.on_connect = on_connect
        mqtt_client.connect(self.broker, self.port)
        return mqtt_client
    
    def subscribe(self, client: mqtt):
        topics_list = [(self.mqtt_feedback_topic, 0), (self.mqtt_setpoint_topic , 0)]
        client.subscribe(topics_list) 
        client.on_message = self.on_message
    
    def on_message(self, client, userdata, msg):
        topic_name = msg.topic.split("/")
        topic_val = msg.payload.decode("utf-8")
        param_list = topic_name[-1].split()
        if "Setpoint" in param_list:
            self.mqtt_set_setpoint(topic_val)
        else:
            self.mqtt_set_feedback(topic_val)
                
    
    def mqtt_start(self):
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_start()

    def set_mqtt_topic_value(self, topic_name: str, value: int):
        # if isinstance(value, int):
        topic = topic_name
        publish.single(topic, str(value), hostname=self.broker)

    def update(self, counts):
        self.set_mqtt_topic_value(self.mqtt_control_topic, counts)

    def calculate_moving_average(self, buffer_size: int, value: float):
        sma = 0
        tmp = 0
        buffer_size_value = buffer_size
        self.mov_av_list.append(value)
        if len(self.mov_av_list) == buffer_size_value:
            for val in self.mov_av_list:
                tmp = tmp + val
            sma = tmp / buffer_size_value
            self.mov_av_list = list()
            print("Moving Average: ", round(sma, 4))
            self.set_mqtt_topic_value(self.mqtt_output_topic, round(sma, 4))
            # return round(sma, 4)
    
    def calculate_median(self, buffer_size: int, value: float):
        median = 0
        tmp = 0
        buffer_size_value = buffer_size
        self.median_list.append(value)
        if len(self.median_list) == buffer_size_value:
            median = statistics.median(self.median_list)
            print("Median: ", round(median, 4))
            self.median_list = list()
            # self.set_mqtt_topic_value(self.mqtt_output_topic, round(median, 4))



def test():
    kp = 16.0
    ki = 3.6
    kd = 6.0
    broker = "192.168.44.11"
    port = 1883
    mqtt_feedback_topic = "/devices/MeasureModule/controls/CH2 Current"
    mqtt_setpoint_topic = "/devices/MeasureModuleSetpoints/controls/CH2 Current Setpoint"
    mqtt_control_topic = "/devices/MeasureModule/controls/CH2 DAC/on"
    pid_test = PIDControl(broker, port, kp=kp, ki=ki, kd=kd, setpoint_topic=mqtt_setpoint_topic,
                          feedback_topic=mqtt_feedback_topic, control_topic=mqtt_control_topic,
                          mqtt_user=None, mqtt_passw=None)
    pid_test.mqtt_start()
    pid_test.run_flag = True
    pid_test.start()
        

if __name__ == "__main__":
    test()
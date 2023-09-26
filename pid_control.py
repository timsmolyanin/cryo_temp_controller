

from simple_pid import PID
from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time


class PIDControl(Thread):
    def __init__(self, parent=None):
        super(PIDControl, self).__init__(parent)
        self.run_flag = False
        self.setpoint = 0.0
        self.feedback = 0.0
        self.broker = "192.168.44.11"
        self.port = 1883
        self.client_id = f'python-mqtt-{random.randint(0, 100)}'
        self.kp = 16.0
        self.ki = 3.6
        self.kd = 6.0
        self.mov_av_list = list()
        self.pid = PID(self.kp, self.ki, self.kd, setpoint=self.setpoint)


    def run(self):
        while self.run_flag:
            time.sleep(0.1)
            calc_counts = self.calc_current_counts(self.setpoint)
            min = calc_counts - self.calc_proc(calc_counts, 2.5)
            max = calc_counts + self.calc_proc(calc_counts, 2.5)
            self.pid.setpoint = self.setpoint
            self.pid.output_limits = (min, max)
            control = self.pid(self.feedback)
            self.update(int(control))
            # print('pid: ', self.setpoint, self.feedback, control)
            sma = self.moving_average(self.feedback)
            print("pid sma: ", sma)

    
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
    
    def set_setpoint(self, setpoint):
        if isinstance(setpoint, str):
            if setpoint == "":
                pass
            else:
                self.setpoint = float(setpoint)
    
    def set_feedback(self, feedback):
        if isinstance(feedback, str):
            if feedback == "":
                pass
            else:
                self.feedback = float(feedback)
    
    def set_run_flag(self, value):
        self.run_flag = value
    

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
        topics_list = [ ("/devices/MeasureModule/controls/CH2 Current", 0),
                        ("/devices/MeasureModuleSetpoints/controls/CH2 Current Setpoint", 0)]
        client.subscribe(topics_list) 
        client.on_message = self.on_message
    
    def on_message(self, client, userdata, msg):
        topic_name = msg.topic.split("/")
        topic_val = msg.payload.decode("utf-8")
        match topic_name[2]:
            case "MeasureModule":
                self.set_feedback(topic_val)
            case "MeasureModuleSetpoints":
                self.set_setpoint(topic_val)
    
    def mqtt_start(self):
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_start()

    def set_current_counts(self, counts: int):
        if isinstance(counts, int):
            topic = "/devices/MeasureModule/controls/CH2 DAC/on"
            publish.single(topic, str(counts), hostname=self.broker)

    def update(self, counts):
        self.set_current_counts(counts)

    def moving_average(self, value: float):
        sma = 0
        tmp = 0
        self.mov_av_list.append(value)
        if len(self.mov_av_list) == 10:
            for val in self.mov_av_list:
                tmp = tmp + val
            sma = tmp / 10
            self.mov_av_list = list()
            return round(sma, 4)

def test():
    pid_test = PIDControl()
    pid_test.mqtt_start()
    pid_test.run_flag = True
    pid_test.start()
    # while True:
    #     time.sleep(0.5)
        

if __name__ == "__main__":
    test()
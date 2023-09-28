

from simple_pid import PID
from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time
import statistics


# The `PIDControl` class is a threaded class that implements a PID controller for a given MQTT broker
# and port, with setpoint, feedback, and control topics, and specified PID parameters.
class PIDControl(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_passw:str,
                    kp:float, ki:float, kd:float, setpoint_topic:str, feedback_topic:str,
                    output_value_topic: str,  control_topic:str, k: float, b: float, limits: float,  parent=None):
        super(PIDControl, self).__init__(parent)
        self.run_flag = False
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.client_id = f"dialtek-mqtt-{random.randint(0, 100)}"
        self.mqtt_setpoint_topic = setpoint_topic
        self.mqtt_feedback_topic = feedback_topic
        self.mqtt_control_topic = control_topic
        self.mqtt_output_topic = output_value_topic
        self.feedback_value = 0.0
        self.setpoint_value = 0.0
        self.buffer_size = 40
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.mov_av_list = list()
        self.median_list = list()
        self.data_filter_type = 2
        self.k = k
        self.b = b
        self.pid_limits_in_percent = limits
        self.control_loop_period = 0.05
        self.pid_auto_mode_value = True
        self.pid = PID(self.kp, self.ki, self.kd, setpoint=self.setpoint_value)


    def run(self):
        """
        The function runs a control loop that calculates control values based on a setpoint and feedback
        value, and updates the control output accordingly, while also performing different calculations
        based on a filter selector.
        """
        while self.run_flag:
            time.sleep(self.control_loop_period)
            self.pid.auto_mode = self.pid_auto_mode_value
            if self.pid_auto_mode_value:
                calculated_counts = self.calculate_control_counts(self.k, self.b, self.setpoint_value)
                min = calculated_counts - self.calculate_value_of_percent(calculated_counts, self.pid_limits_in_percent)
                max = calculated_counts + self.calculate_value_of_percent(calculated_counts, self.pid_limits_in_percent)
                self.pid.setpoint = self.setpoint_value
                self.pid.output_limits = (min, max)
                control = self.pid(self.feedback_value)
                print(self.pid.setpoint, control, self.feedback_value, )
                self.update(int(control))
                match self.data_filter_type:
                    case 0:
                        # send raw values
                        self.set_mqtt_topic_value(self.mqtt_output_topic, self.feedback_value)
                    case 1:
                        # calculate moving average value and send it to mqtt topic
                        self.calculate_moving_average(self.buffer_size, self.feedback_value)
                    case 2:
                        # calculate median value  and send it to mqtt topic
                        self.calculate_median(self.buffer_size, self.feedback_value)

    
    def calculate_control_counts(self, k: float, b: float, x: float) -> int:
        """
        The function calculates the control counts based on a given input value.
        
        :param x: The parameter `x` is a float value that is used in the calculation of `y`
        :type x: float
        :return: an integer value.
        """
        y = k * x + b
        return int(y)


    def calculate_value_of_percent(self, value: int, percent: float) -> int:
        """
        The function calculates the value of a given percentage of a given value.
        
        :param value: The value is an integer representing the initial value or amount
        :type value: int
        :param percent: The percent parameter is a float representing the percentage value. It should be
        a number between 0 and 100
        :type percent: float
        :return: the calculated value of a given percentage of a given value.
        """
        value = (value * percent) / 100
        return int(value)
    

    def mqtt_set_setpoint(self, setpoint: str):
        """
        The function sets the setpoint value for a MQTT client, converting the input to a float if it is
        a non-empty string.
        
        :param setpoint: The `setpoint` parameter is a string that represents the desired setpoint value
        :type setpoint: str
        """
        if isinstance(setpoint, str):
            if setpoint == "":
                self.setpoint_value = 0.0
            else:
                self.setpoint_value = float(setpoint)
        else:
            raise TypeError(f"Type for setpoint must be str, not {type(setpoint)}!")
    

    def mqtt_set_feedback(self, feedback: str):
        """
        The function sets the feedback value based on the input string, converting it to a float if it
        is not empty.
        
        :param feedback: The `feedback` parameter is a string that represents the feedback value
        :type feedback: str
        """
        if isinstance(feedback, str):
            if feedback == "":
                self.feedback_value = 0.0
            else:
                self.feedback_value = float(feedback)
        else:
            raise TypeError(f"Type for feedback must be str, not {type(feedback)}!")
    

    def set_run_flag(self, state: bool):
        """
        The function sets the value of the "run_flag" attribute to the given boolean state, and raises a
        TypeError if the state is not a boolean.
        
        :param state: The `state` parameter is a boolean value that represents the desired state of the
        `run_flag` attribute
        :type state: bool
        """
        if isinstance(state, bool):
            self.run_flag = state
        else:
            raise TypeError(f"Type for state must be bool, not {type(state)}!")


    def set_buffer_size(self, buffer_size: int):
        """
        The function sets the buffer size attribute of an object, raising an error if the input is not
        an integer.
        
        :param buffer_size: The `buffer_size` parameter is an integer that represents the size of the
        buffer
        :type buffer_size: int
        """
        if isinstance(buffer_size, int):
            self.buffer_size = buffer_size
        else:
            raise TypeError(f"Type for buffer_size must be integer, not {type(buffer_size)}!")


    def set_control_loop_period(self, loop_period: float):
        """
        The function sets the control loop period to a specified value, but raises an error if the input
        is not a float.
        
        :param loop_period: The loop_period parameter is a float that represents the time period for the
        control loop
        :type loop_period: float
        """
        if isinstance(loop_period, float):
            self.control_loop_period = loop_period
        else:
            raise TypeError(f"Type for loop_period must be integer, not {type(loop_period)}!")


    def set_pid_limits_in_percent(self, limits: float):
        """
        The function sets the PID limits in percent if the input is a float, otherwise it raises a
        TypeError.
        
        :param limits: The `limits` parameter is a float value that represents the percentage limits for
        the PID controller
        :type limits: float
        """
        if isinstance(limits, float):
            self.pid_limits_in_percent = limits
        else:
            raise TypeError(f"Type for limits must be integer, not {type(limits)}!")


    def set_data_filter_type(self, filter_type: int):
        if isinstance(filter_type, int):
            self.data_filter_type = filter_type
        else:
            raise TypeError(f"Type for filter_type must be integer, not {type(filter_type)}!")


    def connect_mqtt(self) -> mqtt:
        """
        The function `connect_mqtt` connects to an MQTT broker and returns the MQTT client.
        :return: an instance of the MQTT client.
        """
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
        """
        The `subscribe` function subscribes the client to two MQTT topics and sets the `on_message` callback
        function to `self.on_message`.
        
        :param client: The `client` parameter is an instance of the MQTT client that is used to connect to
        the MQTT broker and subscribe to topics
        :type client: mqtt
        """
        topics_list = [(self.mqtt_feedback_topic, 0), (self.mqtt_setpoint_topic , 0)]
        client.subscribe(topics_list) 
        client.on_message = self.on_message
    

    def on_message(self, client, userdata, msg):
        """
        The `on_message` function processes incoming MQTT messages by extracting the topic name and payload,
        splitting the topic name into a list of parameters, and then calling the appropriate function based
        on the presence of a specific parameter.
        
        :param client: The `client` parameter represents the MQTT client object that is used to connect to
        the MQTT broker and publish/subscribe to topics
        :param userdata: The `userdata` parameter is a user-defined data that can be passed to the
        `on_message` function. It can be used to store any additional information or context that you want
        to associate with the MQTT client. This parameter is optional and can be `None` if not needed
        :param msg: The `msg` parameter is the MQTT message received by the client. It contains information
        such as the topic and payload of the message
        """
        topic_name = msg.topic.split("/")
        topic_val = msg.payload.decode("utf-8")
        param_list = topic_name[-1].split()
        if "Setpoint" in param_list:
            self.mqtt_set_setpoint(topic_val)
        else:
            self.mqtt_set_feedback(topic_val)
                
    
    def mqtt_start(self):
        """
        The function `mqtt_start` starts the MQTT client, connects to the MQTT broker, subscribes to
        topics, and starts the client's loop.
        """
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_start()


    def set_mqtt_topic_value(self, topic_name: str, value: int):
        """
        The function sets the value of a specified MQTT topic.
        
        :param topic_name: A string representing the name of the MQTT topic where the value will be
        published
        :type topic_name: str
        :param value: The value parameter is an integer that represents the value you want to publish to
        the MQTT topic
        :type value: int
        """
        topic = topic_name
        publish.single(topic, str(value), hostname=self.broker)


    def update(self, counts):
        """
        The function updates the MQTT topic value with the given counts.
        
        :param counts: The "counts" parameter is a dictionary that contains the updated values for the
        counts
        """
        self.set_mqtt_topic_value(self.mqtt_control_topic, counts)


    def calculate_moving_average(self, buffer_size: int, value: float):
        """
        The `calculate_moving_average` function calculates the moving average of a given value using a
        buffer of a specified size.
        
        :param buffer_size: The `buffer_size` parameter is an integer that represents the size of the buffer
        or window for calculating the moving average. It determines how many values will be included in the
        calculation of the moving average
        :type buffer_size: int
        :param value: The `value` parameter is a float value that represents the current value to be added
        to the moving average calculation
        :type value: float
        """
        sma = 0
        tmp = 0
        buffer_size_value = buffer_size
        self.mov_av_list.append(value)
        if len(self.mov_av_list) == buffer_size_value:
            for val in self.mov_av_list:
                tmp = tmp + val
            sma = tmp / buffer_size_value
            self.mov_av_list = list()
            self.set_mqtt_topic_value(self.mqtt_output_topic, round(sma, 4))
    

    def calculate_median(self, buffer_size: int, value: float):
        """
        The function calculates the median of a list of values and sets the MQTT topic value to the
        rounded median.
        
        :param buffer_size: The parameter `buffer_size` is an integer that represents the size of the
        buffer. It determines how many values will be stored in the `self.median_list` before
        calculating the median
        :type buffer_size: int
        :param value: The `value` parameter is a float value that you want to add to the
        `self.median_list` for calculating the median
        :type value: float
        """
        median = 0
        tmp = 0
        buffer_size_value = buffer_size
        self.median_list.append(value)
        if len(self.median_list) == buffer_size_value:
            median = statistics.median(self.median_list)
            self.median_list = list()
            self.set_mqtt_topic_value(self.mqtt_output_topic, round(median, 4))



def test():
    kp = 16.0
    ki = 3.6
    kd = 6.0
    k = 52.4813
    b = 35.3409
    limi = 2.5
    broker = "192.168.44.11"
    port = 1883
    mqtt_feedback_topic = "/devices/MeasureModule/controls/CH1 Current"
    mqtt_setpoint_topic = "/devices/MeasureModuleSetpoints/controls/CH1 Current Setpoint"
    mqtt_control_topic = "/devices/MeasureModule/controls/CH1 DAC/on"
    mqtt_output_topic = "/devices/FilteredValues/controls/CH1 Current"

    pid_test = PIDControl(broker, port, kp=kp, ki=ki, kd=kd, setpoint_topic=mqtt_setpoint_topic,
                            feedback_topic=mqtt_feedback_topic, control_topic=mqtt_control_topic,
                            output_value_topic=mqtt_output_topic, k=k, b=b, limits=limi,
                            mqtt_user=None, mqtt_passw=None)
    pid_test.mqtt_start()
    pid_test.run_flag = True
    pid_test.start()
    t = 0
    while True:
        time.sleep(0.5)
        t += 1
        print(t)
        if t == 10:
            pid_test.pid_auto_mode_value = False
        

if __name__ == "__main__":
    test()
from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time
import serial
import struct
import yaml

import general_functions
import list_of_mqtt_topics


# The `NextionMqttBridge` class is a thread that connects to a Nextion display via serial
# communication and bridges it with an MQTT broker.
class NextionMqttBridge(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_passw:str,
                 comport_name, comport_baudrate, parent=None):
        super(NextionMqttBridge, self).__init__(parent)
        self.comport = comport_name
        self.baudrate = comport_baudrate
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.client_id = f"dialtek-mqtt-{random.randint(0, 100)}"
        self.comport_open_timeout = 1

        self.aver_buff_size = 5
        self.ch1_temp_list = list()
        self.ch2_temp_list = list()
        self.ch1_fitered_temp_topic = "/devices/FilteredValues/controls/CH1 Temperature"
        self.ch2_fitered_temp_topic = "/devices/FilteredValues/controls/CH2 Temperature"

        self.ldo_current_value = 0.0
        self.ldo_voltage_value = 0.0
        self.ldo_power_value = 0.0
        self.ldo_power_topic = "/devices/FilteredValues/controls/LDO Power"

        params = self.serial_connect(self.comport, self.baudrate)
        self.comport_is_open, self.serial_port = params[0], params[1]

    def run(self):
        """
        The function `run` reads data from a serial port and calls a callback function.
        """
        self.serial_read(self.comport_is_open, self.serial_port, self.nextion_callback)
    

    def serial_connect(self, com: str, baud: int) -> list:
        """
        The function `serial_connect` attempts to establish a serial connection to a specified COM port
        with a given baud rate.
        
        :param com: The "com" parameter is a string that represents the COM port to which you want to
        connect. COM ports are typically used for serial communication with devices such as Arduino
        boards or other serial devices
        :type com: str
        :param baud: The "baud" parameter in the "serial_connect" function is used to specify the baud
        rate for the serial communication. Baud rate refers to the number of signal changes per second
        in a communication channel. It determines the speed at which data is transmitted over the serial
        connection
        :type baud: int
        """
        print("Connect to COM-port")
        comport_is_open = False
        serial_port_obj = None
        while not comport_is_open:
            time.sleep(self.comport_open_timeout)
            try:
                serial_port_obj = serial.Serial(port=com,
                                        baudrate=baud,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        timeout=1)

                comport_is_open = serial_port_obj.isOpen()
                print("Connection is succesfull!", comport_is_open)
            except serial.serialutil.SerialException as exc:
                # TODO: log error
                print("Connection failed", comport_is_open, exc)
                comport_is_open = False

        return [comport_is_open, serial_port_obj]


    def serial_read(self, port_is_open, serial_port_obj, cb):
        """
        The function `serial_read` reads data from a serial port and passes it to a callback function.
        
        :param port_is_open: A boolean variable indicating whether the serial port is open or not
        :param serial_port_obj: The `serial_port_obj` parameter is an object representing the serial
        port that you are reading from. It is used to read data from the serial port using the
        `readline()` method
        :param cb: The parameter "cb" is a callback function that will be called with the decoded data
        from the serial port. It is used to process the received data in some way, such as displaying it
        or performing some action based on it
        """
        while port_is_open:
            if not port_is_open:
                break
            response = ""
            try:
                response = serial_port_obj.readline()
                if response == b'':
                    # Nextion send empty string every second
                    pass
                else:
                    decode_data = response.decode('Ascii')
                    if str(decode_data[-2:]).encode('Ascii') == b'\r\n':
                        # убираем /r/n в конце строки, получается список [decode_data], поэтому отдаем нулевой id
                        cb(decode_data.splitlines()[0])
                        response = ""
            except Exception as exc:
                print("Exception while serial_read method.", exc)
                port_is_open = False
                params = self.serial_connect(self.comport, self.baudrate)
                port_is_open, serial_port_obj = params[0], params[1]


    def serial_write(self, port_is_open, serial_port_obj, cmd):
        """
        The function `serial_write` writes a command to a serial port and handles exceptions if any
        occur.
        
        :param port_is_open: The parameter "port_is_open" is a boolean variable that indicates whether
        the serial port is currently open or not. It is used to check if the port is open before writing
        data to it
        :param serial_port_obj: The `serial_port_obj` parameter is an object representing the serial
        port connection. It is used to write data to the serial port
        :param cmd: The `cmd` parameter is a string that represents the command to be written to the
        serial port. It is encoded using the `encode()` method before being written to the serial port
        object
        """
        eof = struct.pack('B', 0xff)
        if port_is_open:
            try:
                serial_port_obj.write(cmd.encode())
                serial_port_obj.write(eof)
                serial_port_obj.write(eof)
                serial_port_obj.write(eof)
            except Exception as exc:
                print("Exception while serial_write method.", exc)
                port_is_open = False
                params = self.serial_connect(self.comport, self.baudrate)
                port_is_open, serial_port_obj = params[0], params[1]


    def nextion_callback(self, data):
        data_list = data.split("/")
        print(data_list)
        self.set_mqtt_topic_value(f"/devices/{data_list[0]}/controls/{data_list[1]}/on", data_list[-1])
    

    def error_handler(self, error_msg):
        print(error_msg)
        port_is_open = False
        params = self.serial_connect(self.comport, self.baudrate)
        port_is_open, serial_port_obj = params[0], params[1]


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
        try:
            client.subscribe(list_of_mqtt_topics.list_of_mqtt_topics) 
            client.on_message = self.on_message
        except Exception as e:
            print(e)
    
    def calculate_ldo_power(self, voltage: float, current: float, topic_name: str):
        self.ldo_power_value = voltage * current
        self.set_mqtt_topic_value(topic_name, self.ldo_power_value)
    

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
        try:
            match topic_name[2]:
                case "HeaterModule":
                    match topic_name[-1]:
                        case "MEAS Load Current":
                            load_current = round(float(topic_val), 3)
                            self.ldo_current_value = load_current
                            cmd = 'mesurments.t14.txt="' + str(load_current) + '"'
                            self.serial_write(self.comport_is_open, self.serial_port, cmd)
                            self.calculate_ldo_power(self.ldo_voltage_value, self.ldo_current_value, self.ldo_power_topic)
                        case "Output Voltage State":
                            if topic_val == "1":
                                for cmd in general_functions.heater_on_cmds:
                                    self.serial_write(self.comport_is_open, self.serial_port, cmd)
                            elif topic_val == "0":
                                for cmd in general_functions.heater_off_cmds:
                                    self.serial_write(self.comport_is_open, self.serial_port, cmd)
                case "MeasureModule":
                    match topic_name[-1]:
                        case "CH1 Resistance":
                            raw_temp = general_functions.convert_resistanc_to_temp(float(topic_val))
                            self.ch1_temp_list.append(raw_temp[1])
                            if len(self.ch1_temp_list) == self.aver_buff_size:
                                general_functions.calculate_moving_average(self.ch1_temp_list, self.aver_buff_size, self.broker, self.ch1_fitered_temp_topic)
                                self.ch1_temp_list = list()
                        case "CH2 Resistance":
                            raw_temp = general_functions.convert_resistanc_to_temp(float(topic_val))
                            self.ch2_temp_list.append(raw_temp[1])
                            if len(self.ch2_temp_list) == self.aver_buff_size:
                                general_functions.calculate_moving_average(self.ch2_temp_list, self.aver_buff_size, self.broker, self.ch2_fitered_temp_topic)
                                self.ch2_temp_list = list()
                case "FilteredValues":    
                    match topic_name[-1]:
                        case "CH1 Current":
                            current = round(float(topic_val), 3)
                            cmd = 'mesurments.t6.txt="' + str(current) + '"'
                            self.serial_write(self.comport_is_open, self.serial_port, cmd)
                        case "CH2 Current":
                            current = round(float(topic_val), 3)
                            cmd = 'mesurments.t8.txt="' + str(current) + '"'
                            self.serial_write(self.comport_is_open, self.serial_port, cmd)
                        case "LDO Voltage":
                            load_voltage = round(float(topic_val), 3)
                            self.ldo_voltage_value = load_voltage
                            cmd = 'mesurments.t12.txt="' + str(load_voltage) + '"'
                            self.serial_write(self.comport_is_open, self.serial_port, cmd)
                            self.calculate_ldo_power(self.ldo_voltage_value, self.ldo_current_value, self.ldo_power_topic)
                        case "CH1 Temperature":
                            ch1_temp = round(float(topic_val), 2)
                            cmd = 'mesurments.t0.txt="' + str(ch1_temp) + '"'
                            self.serial_write(self.comport_is_open, self.serial_port, cmd)
                        case "CH2 Temperature":
                            ch2_temp = round(float(topic_val), 2)
                            cmd = 'mesurments.t2.txt="' + str(ch2_temp) + '"'
                            self.serial_write(self.comport_is_open, self.serial_port, cmd)
                        case "LDO Power":
                            power = round(float(topic_val), 2)
                            cmd = 'mesurments.t16.txt="' + str(power) + '"'
                            self.serial_write(self.comport_is_open, self.serial_port, cmd)
                case "MeasureModuleSetpoints":
                    match topic_name[-1]:
                        case "CH1 State":
                            if topic_val == "1":
                                for cmd in general_functions.ch1_current_on_cmds:
                                    self.serial_write(self.comport_is_open, self.serial_port, cmd)
                            elif topic_val == "0":
                                for cmd in general_functions.ch1_current_off_cmds:
                                    self.serial_write(self.comport_is_open, self.serial_port, cmd)
                        case "CH2 State":
                            if topic_val == "1":
                                for cmd in general_functions.ch2_current_on_cmds:
                                    self.serial_write(self.comport_is_open, self.serial_port, cmd)
                            elif topic_val == "0":
                                for cmd in general_functions.ch2_current_off_cmds:
                                    self.serial_write(self.comport_is_open, self.serial_port, cmd)
        except Exception as e:
            print(e)
    def mqtt_start(self):
        """
        The function `mqtt_start` starts the MQTT client, connects to the MQTT broker, subscribes to
        topics, and starts the client's loop.
        """
        client = self.connect_mqtt()
        self.subscribe(client)
        client.loop_start()


    def set_mqtt_topic_value(self, topic_name: str, value):
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
            print("Moving Average: ", round(sma, 4))
            self.set_mqtt_topic_value(self.mqtt_output_topic, round(sma, 4))


def test():
    comport = "COM5"
    baudrate = 115200
    broker = "192.168.44.11"
    port = 1883
    nextion_mqtt_bridge = NextionMqttBridge(mqtt_port=port, mqtt_broker=broker, mqtt_passw=None, mqtt_user=None,
                                            comport_baudrate=baudrate, comport_name=comport)
    nextion_mqtt_bridge.mqtt_start()
    nextion_mqtt_bridge.start()


if __name__ == "__main__":
    test()
    
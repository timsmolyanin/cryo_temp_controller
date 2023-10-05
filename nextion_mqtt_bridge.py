from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time
import serial
import struct

import general_functions
import list_of_mqtt_topics

from loguru import logger

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


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
        self.comport_open_timeout = 10

        self.aver_buff_size = 5
        self.ch1_temp_list = list()
        self.ch2_temp_list = list()
        self.ch1_fitered_temp_topic = "/devices/FilteredValues/controls/CH1 Temperature"
        self.ch2_fitered_temp_topic = "/devices/FilteredValues/controls/CH2 Temperature"

        self.ldo_current_value = 0.0
        self.ldo_voltage_value = 0.0
        self.ldo_power_value = 0.0
        self.ldo_power_topic = "/devices/FilteredValues/controls/LDO Power"

        self.__port_is_open = False
        self.__serial_port_obj = None

        self.serial_connect(self.comport, self.baudrate)

    def run(self):
        """
        The function `run` reads data from a serial port and calls a callback function.
        """
        logger.debug(f"Read data from Nextion is started")
        self.serial_read(self.nextion_callback)
    

    def serial_connect(self, com: str, baud: int) -> list:
        """
        """
        logger.debug(f"Conection to Nextion is started")
        serial_port_obj = None
        while not self.__port_is_open:
            try:
                serial_port_obj = serial.Serial(port=com,
                                        baudrate=baud,
                                        parity=serial.PARITY_NONE,
                                        stopbits=serial.STOPBITS_ONE,
                                        bytesize=serial.EIGHTBITS,
                                        timeout=1)

                self.__port_is_open = serial_port_obj.isOpen()
                self.__serial_port_obj = serial_port_obj
                logger.debug(f"Connection is succesfull! {self.__port_is_open}")
            except serial.serialutil.SerialException as exc:
                logger.debug(f"Connection failed {self.__port_is_open}, {exc}")
                self.__port_is_open = False
            if self.__port_is_open:
                return
            else:
                time.sleep(self.comport_open_timeout)


    def serial_read(self, cb):
        """
        """
        while self.__port_is_open:
            if not self.__port_is_open:
                break
            response = ""
            try:
                response = self.__serial_port_obj.readline()
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
                logger.debug(f"Exception while serial_read method. {exc}")
                self.__port_is_open = False
                self.error_handler()


    def serial_write(self, cmd):
        """
        """
        eof = struct.pack('B', 0xff)
        if self.__port_is_open:
            try:
                self.__serial_port_obj.write(cmd.encode())
                self.__serial_port_obj.write(eof)
                self.__serial_port_obj.write(eof)
                self.__serial_port_obj.write(eof)
            except Exception as exc:
                logger.debug(f"Exception while serial_write method. {exc}")
                self.__port_is_open = False


    def nextion_callback(self, data):
        data_list = data.split("/")
        self.set_mqtt_topic_value(f"/devices/{data_list[0]}/controls/{data_list[1]}/on", data_list[-1])
    

    def error_handler(self):
        if not self.__port_is_open:
            self.serial_connect(self.comport, self.baudrate)

    def connect_mqtt(self, whois: str) -> mqtt:
        """
        The function `connect_mqtt` connects to an MQTT broker and returns the MQTT client.
        :return: an instance of the MQTT client.
        """
        logger.debug(f"MQTT client in {whois} started connect to broker")
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.debug(f"{whois} Connected to MQTT Broker!")
            else:
                logger.debug(f"{whois} Failed to connect, return code {rc}")

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
        self.set_mqtt_topic_value(topic_name, round(self.ldo_power_value, 3))
    

    def on_message(self, client, userdata, msg):
        """
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
                            self.serial_write(cmd)
                            self.calculate_ldo_power(self.ldo_voltage_value, self.ldo_current_value, self.ldo_power_topic)
                        case "Output Voltage State":
                            if topic_val == "1":
                                for cmd in general_functions.heater_on_cmds:
                                    self.serial_write(cmd)
                            elif topic_val == "0":
                                for cmd in general_functions.heater_off_cmds:
                                    self.serial_write(cmd)
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
                            self.serial_write(cmd)
                        case "CH2 Current":
                            current = round(float(topic_val), 3)
                            cmd = 'mesurments.t8.txt="' + str(current) + '"'
                            self.serial_write(cmd)
                        case "LDO Voltage":
                            load_voltage = round(float(topic_val), 3)
                            self.ldo_voltage_value = load_voltage
                            cmd = 'mesurments.t12.txt="' + str(load_voltage) + '"'
                            self.serial_write(cmd)
                            self.calculate_ldo_power(self.ldo_voltage_value, self.ldo_current_value, self.ldo_power_topic)
                        case "CH1 Temperature":
                            ch1_temp = round(float(topic_val), 2)
                            cmd = 'mesurments.t0.txt="' + str(ch1_temp) + '"'
                            self.serial_write(cmd)
                        case "CH2 Temperature":
                            ch2_temp = round(float(topic_val), 2)
                            cmd = 'mesurments.t2.txt="' + str(ch2_temp) + '"'
                            self.serial_write(cmd)
                        case "LDO Power":
                            power = round(float(topic_val), 2)
                            cmd = 'mesurments.t16.txt="' + str(power) + '"'
                            self.serial_write(cmd)
                case "MeasureModuleSetpoints":
                    match topic_name[-1]:
                        case "CH1 State":
                            if topic_val == "1":
                                for cmd in general_functions.ch1_current_on_cmds:
                                    self.serial_write(cmd)
                            elif topic_val == "0":
                                for cmd in general_functions.ch1_current_off_cmds:
                                    self.serial_write(cmd)
                        case "CH2 State":
                            if topic_val == "1":
                                for cmd in general_functions.ch2_current_on_cmds:
                                    self.serial_write(cmd)
                            elif topic_val == "0":
                                for cmd in general_functions.ch2_current_off_cmds:
                                    self.serial_write(cmd)
        except Exception as e:
            print(e)

    
    def mqtt_start(self):
        """
        The function `mqtt_start` starts the MQTT client, connects to the MQTT broker, subscribes to
        topics, and starts the client's loop.
        """
        client = self.connect_mqtt("Nextion MQTT Bridge")
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
    
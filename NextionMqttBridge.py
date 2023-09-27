from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time
import serial
import struct

import list_of_mqtt_topics


class NextionMqttBridge(Thread):
    def __init__(self, parent=None):
        super(NextionMqttBridge, self).__init__(parent)
        self.comport = "COM5"
        self.baudrate = 115200
        self.comport_open_timeout = 5
        self.client_id = f'python-mqtt-{random.randint(0, 100)}'
        self.broker = "192.168.44.11"
        self.port = 1883

        params = self.serial_connect(self.comport, self.baudrate)
        self.comport_is_open, self.serial_port = params[0], params[1]

    def run(self):
        self.serial_read(self.comport_is_open, self.serial_port, self.nextion_callback)
    

    def serial_connect(self, com: str, baud: int) -> list:
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
        print(data)
    

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
        print(topic_name, topic_val)
                
    
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


def test():
    nextion_mqtt_bridge = NextionMqttBridge()
    nextion_mqtt_bridge.mqtt_start()
    nextion_mqtt_bridge.start()


if __name__ == "__main__":
    test()
    
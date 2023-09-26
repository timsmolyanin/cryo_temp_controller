import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import serial_port

from threading import Thread
import meta_funcs


class MQTTSubscriberThread(Thread):
    def __init__(self, mqtt_client, host, port, topics_list, comport=None, parent=None):
        super(MQTTSubscriberThread, self).__init__(parent)
        self.mqtt_client = mqtt_client
        self.host = host
        self.port = port
        self.topics_list = topics_list
        # self.logger = logger
        self.mqtt_client.connect(self.host, self.port, 60)
        # self.logger.info("MQTT")

        self.comport = comport

        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        print(self.topics_list)
        self.mqtt_client.subscribe(self.topics_list)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        topic_name = msg.topic.split("/")
        topic_val = msg.payload.decode("utf-8")
        match topic_name[2]:
            case "HeaterModule":
                match topic_name[-1]:
                    case "MEAS LDO REG Vout":
                        load_voltage = round(float(topic_val), 3)
                        cmd = 'mesurments.t12.txt="' + str(load_voltage) + '"'
                        serial_port.serial_write(self.comport, cmd)
                        # print("MEAS LDO REG Vout - ", topic_val)
                    case "MEAS Load Current":
                        load_current = round(float(topic_val), 3)
                        cmd = 'mesurments.t14.txt="' + str(load_current) + '"'
                        serial_port.serial_write(self.comport, cmd)
                        # print("MEAS Load Current - ", topic_val)
                    case "MEAS REG Power":
                        power = round(float(topic_val), 3)
                        cmd = 'mesurments.t16.txt="' + str(power) + '"'
                        serial_port.serial_write(self.comport, cmd)
                        # print("MEAS REG Power - ", topic_val)
                    case "Output Voltage State":
                        if topic_val == "1":
                            for cmd in meta_funcs.heater_on_cmds:
                                serial_port.serial_write(self.comport, cmd)
                        elif topic_val == "0":
                            for cmd in meta_funcs.heater_off_cmds:
                                serial_port.serial_write(self.comport, cmd)
            case "MeasureModule":
                match topic_name[-1]:
                    case "CH1 Resistance":
                        t = meta_funcs.convert_resistanc_to_temp(float(topic_val))
                        cmd = 'mesurments.t0.txt="' + str(t[1]) + '"'
                        serial_port.serial_write(self.comport, cmd)
                        # print("CH1 Resistance ", topic_val)
                        # print("CH1 Temperature ", t[0], " C")
                        # print("CH1 Temperature ", t[1], " K")
                    case "CH2 Resistance":
                        t = meta_funcs.convert_resistanc_to_temp(float(topic_val))
                        cmd = 'mesurments.t2.txt="' + str(t[1]) + '"'
                        serial_port.serial_write(self.comport, cmd)
                        # print("CH2 Resistance ", topic_val)
                        # print("CH2 Temperature ", t[0], " C")
                        # print("CH2 Temperature ", t[1], " K")
                    case "CH1 Current":
                        current = round(float(topic_val), 3)
                        cmd = 'mesurments.t6.txt="' + str(current) + '"'
                        serial_port.serial_write(self.comport, cmd)
                    case "CH2 Current":
                        current = round(float(topic_val), 3)
                        cmd = 'mesurments.t8.txt="' + str(current) + '"'
                        serial_port.serial_write(self.comport, cmd)
    def run(self):
        while True:
            try:
                self.mqtt_client.loop_forever()
            except Exception as exc:
                print("mqtt thread run", exc)


def _test_main():
    # publish.single("/devices/outletcontrol_34/controls/OutletGroup1/on", 0, hostname="192.168.44.10")
    # wb_mqtt_switch()
    # client = mqtt.Client()
    # mqtt_subscribe_topics = "/devices/outletcontrol_34/controls/OutletGroup1"
    # mqtt_test = MQTTSubscriberThread(client, "192.168.4.9", 1883, mqtt_subscribe_topics)
    # mqtt_test.setDaemon(True)
    # mqtt_test.start()
    pass


if __name__ == "__main__":
    _test_main()

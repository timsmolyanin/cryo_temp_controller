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


from list_of_mqtt_topics import mqtt_topics_system_module

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


class SystemModule(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_password:str, parent=None):
        
        super(SystemModule, self).__init__(parent)
        self.name = "system_module"
        self.topic_list = mqtt_topics_system_module
        self.on_message_config = {
            self.topic_list["input_wifi_state"] : self.set_wifi_state,
            self.topic_list["input_wifi_mode"] : self.set_wifi_mode,
            self.topic_list["input_wifi_client_ssid"] : self.set_wifi_client_ssid,
            self.topic_list["input_wifi_client_password"] : self.set_wifi_client_password,
            self.topic_list["input_wifi_hotspot_ssid"] : self.set_wifi_hotspot_ssid,
            self.topic_list["input_wifi_hotspot_password"] : self.set_wifi_hotspot_password,
            self.topic_list["input_eth_mode"] : self.set_eth_mode,
            self.topic_list["input_eth_ip"] : self.set_eth_ip,
            self.topic_list["input_eth_mask"] : self.set_eth_mask,
            self.topic_list["input_eth_gateway"] : self.set_eth_gateway,
            self.topic_list["input_update_files_list"] : self.update_file_list          #/root/wk/measure_module/Sensors/ConfigFolder
        }
        
        self.mqtt = mqtt_module.Mqtt(mqtt_broker, mqtt_port, mqtt_user, mqtt_password, self.name, self.on_message_config, self.topic_list)
        self.mqtt.start()
        
        self.wifi_state = 1
        self.wifi_mode = ""
        
        self.wifi_client_ssid = ""
        self.wifi_client_password = ""
        
        self.wifi_hotspot_ssid = ""
        self.wifi_hotspot_password = ""
        
        self.eth_mode = ""
        self.eth_ip = ""
        self.eth_mask = ""
        self.eth_gateway = ""
        
    def update_file_list(self, value):
        directory_path = "/root/wk/measure_module/Sensors/ConfigFolder"
        file_list = os.listdir(directory_path)
        logger.debug(f"Список файлов в директории:")
        term = "\r\n"
        result = ""
        for each in file_list:
            result += f"{each}{term}"
        logger.debug(f"Строка для топика: {result}")
        self.mqtt.publish_topic(self.topic_list["output_update_files_list"], result)
            
    def set_wifi_state(self, value):
        self.wifi_state = int(value)
        if self.wifi_state == 0:
            # self.wifi_adapter_off()
            return
        if self.wifi_state == 1:
            # self.wifi_adapter_on()
            return
    
    def wifi_adapter_off(self):
        nmcli.radio.wifi_off()
        logger.debug(f"{self.name}: Wifi adapter is OFF")
        
    def wifi_adapter_on(self):
        nmcli.radio.wifi_on()
        self.delete_wifi_conn()
        logger.debug(f"{self.name}: Wifi adapter is ON")
    
    def set_wifi_client_ssid(self, value):
        self.wifi_client_ssid = str(value)
        
    def set_wifi_client_password(self, value):
        self.wifi_client_password = str(value)
        
    def set_wifi_hotspot_ssid(self, value):
        self.wifi_hotspot_ssid = str(value)
        
    def set_wifi_hotspot_password(self,value):
        self.wifi_hotspot_password = str(value)
    
    def set_wifi_mode(self, mode):
        if mode == "client":
            self.wifi_mode = self.wifi_client_mode
            
        if mode == "hotspot":
            self.wifi_mode = self.wifi_hotspot_mode
        
        self.wifi_mode()
    
    def set_eth_mode(self, mode):
        if mode == "static":
            self.eth_mode = self.eth_static_mode
            
        if mode == "dhcp":
            self.eth_mode = self.eth_dhcp_mode
            
        self.eth_mode()
    
    def set_eth_ip(self, value):
        self.eth_ip = str(value)
    
    def set_eth_mask(self, value):
        self.eth_mask = str(value)
    
    def set_eth_gateway(self, value):
        self.eth_gateway = str(value)
    
    def delete_wifi_conn(self):
        for conn in nmcli.connection():
            if conn.conn_type == 'wifi':
                try:
                    nmcli.connection.delete(name=conn.name)
                except Exception as exc:
                    print(exc)
    
    def show_wifi_connections(self):
        for conn in nmcli.connection():
            if conn.conn_type == 'wifi':
                try:
                    print(conn)
                    print(type(conn))
                except Exception as exc:
                    print(exc)
                
    def eth_static_mode(self):
        logger.debug("Выполняется настройка статического IP адреса без шлюза")
        static_ip = f"{self.eth_ip}/{self.eth_mask}"
        cidr_str = str(ipaddress.ip_interface(static_ip))
        nmcli.connection.modify("eth_port", {
            "ipv4.addresses": cidr_str,
            "ipv4.method": "manual"
        })
        nmcli.connection.down("eth_port")
        nmcli.connection.up("eth_port")
        # else:
        #     logger.debug("Выполняется настройка статического IP адреса с указанием шлюза")
        #     nmcli.connection.modify("wb-eth1", {
        #         "ipv4.addresses": f"{self.eth_ip}/{self.eth_mask}",
        #         "ipv4.gateway": f"{self.eth_gateway}",
        #         "ipv4.method": "manual"
        #     })
    
    def eth_dhcp_mode(self):
        logger.debug("Выполняется получение IP адреса от сервера DHCP")
        nmcli.connection.modify('eth_port', {
            "ipv4.address": "",
            "ipv4.method": "auto"
        })
        nmcli.connection.down("eth_port")
        nmcli.connection.up("eth_port")
    
    def wifi_client_mode(self):
        print(self.wifi_client_ssid)
        print(self.wifi_client_password)
        self.wifi_adapter_on()
        try:
            logger.debug(f'Подключение к Wi-Fi сети "{self.wifi_client_ssid}", используя пароль "{self.wifi_client_password}"')
            nmcli.device.wifi_connect(ssid=self.wifi_client_ssid, password=self.wifi_client_password)
            self.show_wifi_connections()
            nmcli.connection.up(self.wifi_client_ssid)
            logger.debug(f'Успешное подключение')
        except Exception as exception:
            logger.debug("Ошибка при подключении к сети:")
            logger.debug(f"{exception}")
    
    def wifi_hotspot_mode(self):
        print(self.wifi_hotspot_ssid)
        print(self.wifi_hotspot_password)
        self.wifi_adapter_on()
        try:
            logger.debug(f'Создание точки доступа сети "{self.wifi_hotspot_ssid}", c паролем "{self.wifi_hotspot_password}"')
            nmcli.device.wifi_hotspot(ssid=self.wifi_hotspot_ssid, password=self.wifi_hotspot_password)
            nmcli.connection.modify('Hotspot',{
                'connection.autoconnect' : "yes",
                "ipv4.method": "shared"
            })
            # self.show_wifi_connections()
            nmcli.connection.up("Hotspot")
            logger.debug(f'Точка доступа создана')
        except Exception as exception:
            logger.debug("Ошибка при создании точки доступа:")
            logger.debug(f"{exception}")
            
    def wifi_scan(self):
        logger.debug('Список доступных сетей:')
        result = []
        for each in str(nmcli.device.wifi()).split(", "):
            if "ssid" in each:
                if "bssid" not in each:
                    if each not in result:
                        result.append(each)
                        logger.debug(f'    {each.replace("ssid=","")}')
            

def test():
    broker = "127.0.0.1"
    # broker = "192.168.44.11"
    port = 1883
    test = SystemModule(broker, port, 'abc', 'abc')
    while True:
        time.sleep(1)


if __name__ == "__main__":
    test()
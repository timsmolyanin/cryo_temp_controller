

from threading import Thread
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import mqtt_module
import yaml
import os
import nmcli
from loguru import logger


from list_of_mqtt_topics import mqtt_topics_system_module

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

# The `PIDControl` class is a threaded class that implements a PID controller for a given MQTT broker
# and port, with setpoint, feedback, and control topics, and specified PID parameters.
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
        
        self.wifi_state = 0
        self.wifi_mode = None
        
        self.wifi_client_ssid = None
        self.wifi_client_password = None
        
        self.wifi_hotspot_ssid = None
        self.wifi_hotspot_password = None
        
        self.eth_mode = None
        self.eth_ip = None
        self.eth_mask = None
        self.eth_gateway = None
        
    def update_file_list(self):
        directory_path = "/root/wk/measure_module/Sensors/ConfigFolder"
        file_list = os.listdir(directory_path)
        logger.debug(f"Список файлов в директории:")
        
        result = ""
        for each in file_list:
            result += each + '\\r\\'
            logger.debug(f"    {each}")
        result += 'n'
        logger.debug(f"Строка для топика: {result}")
        self.mqtt.publish_topic(self.topic_list["output_update_files_list"], result)
            
            
            
        
    def set_wifi_state(self, value):
        self.wifi_state = int(value)
        if self.wifi_state == 0:
            self.wifi_adapter_off()
            return
        if self.wifi_state == 1:
            self.wifi_adapter_on()
            pass
    
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
                
    def eth_static_mode(self):
        if self.eth_gateway == "None":
            logger.debug("Выполняется настройка статического IP адреса без шлюза")
            nmcli.connection.modify("wb-eth0", {
                "ipv4.addresses": f"{self.eth_ip}/{self.eth_mask}",
                "ipv4.method": "manual"
            })
        else:
            logger.debug("Выполняется настройка статического IP адреса с указанием шлюза")
            nmcli.connection.modify("wb-eth0", {
                "ipv4.addresses": f"{self.eth_ip}/{self.eth_mask}",
                "ipv4.gateway": f"{self.eth_gateway}",
                "ipv4.method": "manual"
            })
    
    def eth_dhcp_mode(self):
        logger.debug("Выполняется получение IP адреса от сервера DHCP")
        nmcli.connection.modify('wb-eth0', {
            "ipv4.method": "auto"
        })
    
    def wifi_client_mode(self):
        try:
            logger.debug(f'Подключение к Wi-Fi сети "{self.wifi_client_ssid}", используя пароль "{self.wifi_client_password}"')
            nmcli.device.wifi_connect(ssid=self.wifi_client_ssid, password=self.wifi_client_password)
            logger.debug(f'Успешное подключение')
        except Exception as exception:
            logger.debug("Ошибка при подключении к сети:")
            logger.debug(f"{exception}")
    
    def wifi_hotspot_mode(self):
        try:
            logger.debug(f'Создание точки доступа сети "{self.wifi_hotspot_ssid}", c паролем "{self.wifi_hotspot_password}"')
            nmcli.device.wifi_hotspot(ssid=self.wifi_hotspot_ssid, password=self.wifi_hotspot_password)
            nmcli.connection.modify('Hotspot',{
                'connection.autoconnect' : "yes"
            })
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
            

#system_module = SystemModule("test", 1, "test", "test")
#Вай фай (клиент)
# system_module.set_wifi_client_ssid("TP-Link_B99E")
# system_module.set_wifi_client_password("lhep201-316")
# system_module.set_wifi_state(0)
# system_module.set_wifi_state(1)
# time.sleep(10)
# system_module.wifi_scan()
# system_module.set_wifi_mode("client")

#Вай фай (хост)
# system_module.set_wifi_hotspot_ssid("Wirenboard controller")
# system_module.set_wifi_hotspot_password("tangompd")
# system_module.set_wifi_state(0)
# system_module.set_wifi_state(1)
# time.sleep(5)
# system_module.set_wifi_mode("hotspot")

#Получить список файлов из директории
#system_module.update_file_list()





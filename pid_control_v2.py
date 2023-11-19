

from simple_pid import PID
from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time
import statistics
from loguru import logger

# Теперь у нас будет один файл со всеми списками топиков, которые нам нужны            <---NEW--->
from list_of_mqtt_topics import mqtt_topics_pid

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

# The `PIDControl` class is a threaded class that implements a PID controller for a given MQTT broker
# and port, with setpoint, feedback, and control topics, and specified PID parameters.
class PIDControl(Thread):
    def __init__(self, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_passw:str,
                    kp:float, ki:float, kd:float, topic_list: dict,
                    parent=None):
        
        super(PIDControl, self).__init__(parent)
        
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.client = ""
        self.client_id = f"dialtek-mqtt-{random.randint(0, 100)}"
        
        self.topic_list = topic_list
        
        self.input_value = 0.0
        self.setpoint_value = 0.0
        self.over_regulation_percent = 1
        self.state = 0

        self.__measurements_buffer_size = 5
        self.__measurements_buffer = []
        
        # self.__kp = kp
        # self.__ki = ki
        # self.__kd = kd
        self.__kp = 7826.9163248793075
        self.__ki = 25.267158409925372
        self.__kd = 0.0
        
        self.__control_loop_period = 1
        
        self.__pid_min = 0.0
        self.__pid_max = 20.0

        self.__pid = PID(self.__kp, self.__ki, self.__kd, setpoint=self.setpoint_value, output_limits=(self.__pid_min * 1310.7, self.__pid_max * 1310.7))
        
        self.name = "PID_control_v2"
        
    def parse_buffer(self, buffer):
        #Идёт ли разогрев
        for i in range(len(buffer) - 1):
            if buffer[i + 1] > buffer[i]:
                if i == (len(buffer) - 2):
                    return "In process Up"
            else:
                break
        
        #Охлаждение
        for i in range(len(buffer) - 1):
            if buffer[i + 1] < buffer[i]:
                if i == (len(buffer) - 2):
                    return "In process Down"
            else:
                break
        
        #Достаточно ли напряжения
        for i in range(len(buffer)):
            if buffer[i] < self.setpoint_value:
                if i == (len(buffer) - 1):
                    return "PID limits Error"
            else:
                break
        
        #Есть ли перерегулирование
        for i in range(len(buffer)):
            if (buffer[i] - self.setpoint_value) > (self.setpoint_value * (self.over_regulation_percent / 100)):
                if i == (len(buffer) - 1):
                    return "Over-regulation"
            else:
                break
        
        #Всё впорядке
        for i in range(len(buffer)):
            if abs(buffer[i] - self.setpoint_value) <= (self.setpoint_value * (self.over_regulation_percent / 100)):
                if i == (len(buffer) - 1):
                    return "Ok"
            else:
                break
        return "Unexpected case"
                
                                         
    #Наверное здесь ещё нужно публиковать топик, который в дисплее будет уведомлять, что у нас режим ожидания
    def mode_wait(self):
        pass    

                                         
    def mode_control(self):

        #PID'уем
        self.mqtt_publish_topic(self.topic_list["output_value"], int(self.__pid(self.input_value)))
        logger.debug(f"{self.__pid(self.input_value)} - Значение, которое выдал PID регулятор")
        
        #Копируем буфер, чтобы во время парсинга он не менялся
        buffer = self.__measurements_buffer.copy()
        
        #Если не хватает значений, то просто в логгер записываем кол-во элементов в буфере и сам буфер
        if len(buffer) < self.__measurements_buffer_size:
            logger.debug(f"Значений в буфере: {len(buffer)} / {self.__measurements_buffer_size}")
            logger.debug(f"Буфер: {buffer}")
            return
        #Если значений хватает, то вызываем parse_buffer, он вёрнёт нам состояние, отталкиваясь от него мы что-то делаем
        else:
            self.__measurements_buffer = []
            parse_result = self.parse_buffer(buffer)
            match parse_result:
                case "In process Up":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "In process Down":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "PID limits Error":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "Over-regulation":
                    
                    self.mqtt_publish_topic(self.topic_list["output_state"], 0)
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "Ok":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "Unexpected case":
                    logger.debug(f"Состояние: {parse_result}")
                    logger.debug(f"Буфер: {buffer}")
                    return

    
    def mode_tuning(self):
        #Какие-то действия 
        self.set_pid_tunings(self)
        pass
    
    def mode_test(self):
        #Тело метода
        pass
                                      
    def set_run_mode(self, mode):
        self.run_mode = mode
        pass   
    
           
    def run(self):
        #Логгер
        logger.debug(f"Regulator {self.name} is started")
        
        #Выбираем режим управления
        self.set_run_mode(self.mode_wait)
        logger.debug("Включен режим ожидания")
        
        while True:
            #Вызываем текущий режим управления
            self.run_mode()
            
            #Sleep
            time.sleep(self.__control_loop_period)


    def set_pid_limits(self, min: float, max: float):
        self.__pid_min = min 
        self.__pid_max = max
        self.__pid.output_limits = (self.__pid_min * 1310.7, self.__pid_max * 1310.7)
    
    def set_pid_kp_value(self, value):
        
        self.__kp = float(value)
        self.__pid.Kp = self.__kp
        
    def set_pid_ki_value(self, value):
        
        self.__ki = float(value)
        self.__pid.Ki = self.__ki
        
        
    def set_pid_kd_value(self, value):
        
        self.__kd = float(value)
        self.__pid.Kd = self.__kd
    
    def set_pid_tunings(self):
        
        self.__pid.tunings(self.__kp, self.__ki, self.__kd)  



    def set_setpoint_value(self, setpoint):
        self.setpoint_value = float(setpoint)
        self.__pid.setpoint = self.setpoint_value
        self.__measurements_buffer.clear()
        logger.debug(f"setpoint_value = {float(self.setpoint_value)}")
    
    def set_input_value(self, value):
        self.input_value = value
        self.__measurements_buffer.append(value)
    

    def set_buffer_size(self, buffer_size):

        self.__measurements_buffer_size = int(buffer_size)


    def set_control_loop_period(self, loop_period: float):
        
        self.__control_loop_period = float(loop_period)
        
        




    def connect_mqtt(self, whois: str) -> mqtt:
        """
        The function `connect_mqtt` connects to an MQTT broker and returns the MQTT client.
        :return: an instance of the MQTT client.
        """
        logger.debug(f"MQTT client in {whois} started connect to broker")
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.debug(f"{whois} Connected to MQTT Broker!")
                return
            else:
                logger.debug(f"{whois} Failed to connect, return code {rc}")

        mqtt_client = mqtt.Client(self.client_id)
        mqtt_client.on_connect = on_connect
        mqtt_client.connect(self.broker, self.port)
        return mqtt_client
    
    def unsubscribe(self, client: mqtt):
        
        for key, value in self.topic_list.items():
            if not "output" in key:
                client.unsubscribe(value)
    

    def subscribe(self, client: mqtt):
        
        for key, value in self.topic_list.items():
            if not "output" in key:
                client.subscribe(value)
        client.on_message = self.on_message
        
    def change_topic(self, topic_to_change, topic):
        
        self.unsubscribe(self.client)
        
        self.topic_list[topic_to_change[13:]] = topic

        
        self.subscribe(self.client)
    
    def get_key_by_value(self, value):
        for key, v in self.topic_list.items():
            if v == value:
                return key
        
    def set_state(self, value):
        self.state = int(value)
        if self.state == 0:
            self.set_run_mode(self.mode_wait)
            self.mqtt_publish_topic(self.topic_list["output_value"], 0)
            logger.debug("Включен режим ожидания")
        if self.state == 1:
            self.set_run_mode(self.mode_control)
            logger.debug("Включен режим управления")
        self.__measurements_buffer.clear()
    
    def on_message(self, client, userdata, msg):
        
        config = {
            self.topic_list["input_setpoint_value"] : self.set_setpoint_value,
            self.topic_list["input_value"] : self.set_input_value,
            self.topic_list["input_state"] : self.set_state,
            self.topic_list["input_PID_values_P_value"] : self.set_pid_kp_value,
            self.topic_list["input_PID_values_I_value"] : self.set_pid_ki_value,
            self.topic_list["input_PID_values_D_value"] : self.set_pid_kd_value,
        }
        
        topic_name = msg.topic 
        topic_value = msg.payload.decode("utf-8")
        
        if ("change_topic" in self.get_key_by_value(topic_name)):
            self.change_topic(self.get_key_by_value(topic_name), topic_value)
        else:
            config[topic_name](float(topic_value))
            
        
        
        
        

                
    def mqtt_start(self):
        
        self.client = self.connect_mqtt(self.name)
        self.subscribe(self.client)
        self.client.loop_start()

    #Публикует топик с именем topic_name и значением topic_value
    def mqtt_publish_topic(self, topic_name, topic_value):
        
        publish.single(str(topic_name), str(topic_value), hostname=self.broker)
    
    



def test():
    kp = 16.0
    ki = 3.6
    kd = 6.0
    broker = "192.168.44.11"
    port = 1883


    pid_test = PIDControl(broker, port, kp=kp, ki=ki, kd=kd, topic_list = mqtt_topics_pid, mqtt_user=None, mqtt_passw=None)
    pid_test.mqtt_start()
    pid_test.start()
        

if __name__ == "__main__":
    test()
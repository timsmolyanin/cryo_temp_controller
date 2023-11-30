from simple_pid import PID
from threading import Thread
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import random
import time
from loguru import logger

# Теперь у нас будет один файл со всеми списками топиков, которые нам нужны            <---NEW--->
#from list_of_mqtt_topics import mqtt_topics_current_ch1_pid, mqtt_topics_current_ch2_pid, mqtt_topics_heater_pid
from list_of_mqtt_topics import mqtt_topics_heater_pid
#from list_of_mqtt_topics import mqtt_topics_current_ch1_pid, mqtt_topics_current_ch2_pid, mqtt_topics_heater_pid
from list_of_mqtt_topics import mqtt_topics_heater_pid

logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

# The `PIDControl` class is a threaded class that implements a PID controller for a given MQTT broker
# and port, with setpoint, feedback, and control topics, and specified PID parameters.
class PIDControl(Thread):
    def __init__(self, mqtt_topic_list, mqtt_broker:str, mqtt_port:int, mqtt_user: str, mqtt_password: str, pid_max_range: int, kp, ki, kd, parent=None):
        
        super(PIDControl, self).__init__(parent)
        
        self.broker = mqtt_broker
        self.port = mqtt_port
        self.client = ""
        self.client_id = f"dialtek-mqtt-{random.randint(0, 100)}"
        
        self.topic_list = mqtt_topic_list
        
        self.input_value = 0.0
        self.setpoint_value = 0.0
        self.over_regulation_percent = 1
        self.state = 0

        self.__measurements_buffer_size = 5
        self.__measurements_buffer = []
        
        # self.pid_max_range = 65535
        self.pid_max_range = pid_max_range
        self.__kp = kp
        self.__ki = ki
        self.__kd = kd
        # self.__kp = 7826.9163248793075
        # self.__ki = 25.267158409925372
        # self.__kd = 0.0
        
        self.__control_loop_period = 1
        
        self.__pid_max = 50
        self.__pid_min = 0
        self.__pid_k = 0 #1310,7

        self.__pid = PID(self.__kp, self.__ki, self.__kd, setpoint=self.setpoint_value, output_limits=(0, self.pid_max_range))
        self.iterations_to_skip_after_start = 2
        self.current_iteration = 0
        
        self.name = "PID_control"
        
    def parse_buffer(self, buffer):

        #Есть ли перерегулирование
        for i in range(len(buffer)):
            if (buffer[i] - self.setpoint_value) > (self.setpoint_value * (self.over_regulation_percent / 100)):
                if i == (len(buffer) - 1):
                    return "Over-regulation"
            else:
                break

        #Идёт ли разогрев
        for i in range(len(buffer) - 1):
            if buffer[i + 1] >= buffer[i]:
                if i == (len(buffer) - 2):
                    return "In process Up"
            else:
                break
        
        
                
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

        #Всё впорядке
        for i in range(len(buffer)):
            if abs(buffer[i] - self.setpoint_value) <= (self.setpoint_value * (self.over_regulation_percent / 100)):
                if i == (len(buffer) - 1):
                    return "Ok"
            else:
                break

        #Достаточно ли напряжения
        for i in range(len(buffer)):
            if buffer[i] < self.setpoint_value:
                if i == (len(buffer) - 1) and int(self.__pid(self.input_value)) == self.__pid.output_limits[1]:
                    return "PID limits Error"
            else:
                break

        return "Unexpected case"
                
                                         
    #Наверное здесь ещё нужно публиковать топик, который в дисплее будет уведомлять, что у нас режим ожидания
    def mode_wait(self):
        self.mqtt_publish_topic(self.topic_list["output_state_str"], "Нагрев выключен")
        self.current_iteration = 0
        pass    

                                         
    def mode_control(self):

        #PID'уем
        self.mqtt_publish_topic(self.topic_list["output_value"], int(self.__pid(self.input_value)))
        logger.debug(f"Значение PID: {self.__pid(self.input_value)}")
        
        #Копируем буфер, чтобы во время парсинга он не менялся
        buffer = self.__measurements_buffer.copy()
        
        #Если не хватает значений, то просто в логгер записываем кол-во элементов в буфере и сам буфер
        if len(buffer) < self.__measurements_buffer_size:
            return
        
        
        if self.current_iteration < self.iterations_to_skip_after_start:
            self.current_iteration = self.current_iteration + 1
            self.__measurements_buffer.clear()
            return
        #Если значений хватает, то вызываем parse_buffer, он вёрнёт нам состояние, отталкиваясь от него мы что-то делаем
        else:
            logger.debug(f"Буфер: {buffer}")
            installation_percent = round( (self.input_value / self.setpoint_value) * 100)
            logger.debug(f"Процент уставки: {installation_percent}")
            self.__measurements_buffer = []
            parse_result = self.parse_buffer(buffer)
            match parse_result:
                case "In process Up":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    self.mqtt_publish_topic(self.topic_list["output_state_str"], parse_result + " " + str(installation_percent) + "%")
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "In process Down":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    self.mqtt_publish_topic(self.topic_list["output_state_str"], parse_result + " " + str(installation_percent) + "%")
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "PID limits Error":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    self.mqtt_publish_topic(self.topic_list["output_state_str"], parse_result + " " + str(installation_percent) + "%")
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "Over-regulation":
                    
                    self.mqtt_publish_topic(self.topic_list["output_state"], 0)
                    self.mqtt_publish_topic(self.topic_list["output_state_str"], parse_result + " " + str(installation_percent) + "%")
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "Ok":
                    #mqtt_publish_topic(self, <имя топика?>, parse_result)
                    self.mqtt_publish_topic(self.topic_list["output_state_str"], parse_result + " " + str(installation_percent) + "%")
                    logger.debug(f"Состояние: {parse_result}")
                    return
                case "Unexpected case":
                    logger.debug(f"Состояние: {parse_result}")
                    self.mqtt_publish_topic(self.topic_list["output_state_str"], parse_result + " " + str(installation_percent) + "%")
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
        logger.debug(f"Регулятор {self.name} запущен")
        
        #Выбираем режим управления
        self.set_run_mode(self.mode_wait)
        logger.debug("Включен режим ожидания")
        
        while True:
            #Вызываем текущий режим управления
            self.run_mode()
            
            #Sleep
            time.sleep(self.__control_loop_period)


    def set_pid_limits_max(self, value):
        self.__pid_max = float(value) #50
        self.__pid_k = self.pid_max_range / (self.__pid_max - self.__pid_min) #65535 / (max - min)
        logger.debug(f'Значение верхней границы (В) ПИД регулятора установлено на: {float(value)}')
        
    def set_pid_limits_min(self, value):
        self.__pid_min = float(value)
        self.__pid_k = self.pid_max_range / (self.__pid_max - self.__pid_min) 
    
    def set_pid_current(self, value):
        self.__pid.output_limits = (0, float(value) * self.__pid_k)
        logger.debug(f'Максимальное значение ПИД (В) установлено на: {float(value)}')
        logger.debug(f'Максимальное значение ПИД (В * коэффициент) установлено на: {float(value) * self.__pid_k}')
   
    
    def set_pid_kp_value(self, value):
        
        self.__kp = float(value)
        self.__pid.Kp = self.__kp
        logger.debug(f'Значение коэффициента P установлено на: {float(value)}')

        
    def set_pid_ki_value(self, value):
        
        self.__ki = float(value)
        self.__pid.Ki = self.__ki
        logger.debug(f'Значение коэффициента I установлено на: {float(value)}')
        
        
    def set_pid_kd_value(self, value):
        
        self.__kd = float(value)
        self.__pid.Kd = self.__kd
        logger.debug(f'Значение коэффициента D установлено на: {float(value)}')
    
    def set_pid_tunings(self):
        
        self.__pid.tunings(self.__kp, self.__ki, self.__kd)  

    def set_setpoint_value(self, setpoint):
        self.setpoint_value = float(setpoint)
        self.__pid.setpoint = self.setpoint_value
        self.__measurements_buffer.clear()
        logger.debug(f"Значение уставки установлено на: {float(self.setpoint_value)}")
    
    def set_input_value(self, value):
        if self.run_mode != self.mode_wait:
            self.input_value = float(value)
            self.__measurements_buffer.append(self.input_value)
            #logger.debug(f"Значений в буфере: {len(self.__measurements_buffer)} / {self.__measurements_buffer_size}")

    

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
            self.mqtt_publish_topic(self.topic_list["output_state_str"], "Запуск")
            
        self.__measurements_buffer.clear()
    
    def on_message(self, client, userdata, msg):
        
        config = {
            self.topic_list["input_setpoint_value"] : self.set_setpoint_value,
            self.topic_list["input_value"] : self.set_input_value,
            self.topic_list["input_state"] : self.set_state,
            self.topic_list["input_pid_current"] : self.set_pid_current, 
            self.topic_list["input_PID_values_P_value"] : self.set_pid_kp_value,
            self.topic_list["input_PID_values_I_value"] : self.set_pid_ki_value,
            self.topic_list["input_PID_values_D_value"] : self.set_pid_kd_value,
        }
        
        topic_name = msg.topic 
        topic_value = msg.payload.decode("utf-8")
        
        if ("change_topic" in self.get_key_by_value(topic_name)):
            self.change_topic(self.get_key_by_value(topic_name), topic_value)
        else:
            try:
                config[topic_name](topic_value)
            except Exception as ex:
                logger.debug(f"{self.name}: Ошибка в исполнении топика - {topic_name}")
                logger.debug(f"А имеено: {ex}")
                
    def mqtt_start(self):
        self.client = self.connect_mqtt(self.name)
        self.subscribe(self.client)
        self.client.loop_start()

    #Публикует топик с именем topic_name и значением topic_value
    def mqtt_publish_topic(self, topic_name, topic_value):
        
        publish.single(str(topic_name), str(topic_value), hostname=self.broker)
    
    



def test():
    broker = "192.168.44.11"
    port = 1883

    pid_heater_test = PIDControl(mqtt_topics_heater_pid, broker, port, mqtt_user=None, mqtt_password=None, pid_max_range=65535, ki=0, kd=0, kp=0)
    pid_heater_test.set_pid_limits_min(0)
    pid_heater_test.set_pid_limits_max(50)
    pid_heater_test.mqtt_start()
    pid_heater_test.start()

    # pid_current_ch1_test = PIDControl(mqtt_topics_current_ch1_pid, broker, port, mqtt_user=None, mqtt_password=None, pid_max_range=65535, ki=0, kd=0, kp=0)
    # pid_current_ch1_test.set_pid_limits_min(0)
    # pid_current_ch1_test.set_pid_limits_max(950)
    # pid_current_ch1_test.mqtt_start()
    # pid_current_ch1_test.start()

    # pid_current_ch2_test = PIDControl(mqtt_topics_current_ch1_pid, broker, port, mqtt_user=None, mqtt_password=None, pid_max_range=30000, ki=0, kd=0, kp=0)
    # pid_current_ch2_test.mqtt_start()
    # pid_current_ch2_test.start()

    
        

if __name__ == "__main__":
    test()
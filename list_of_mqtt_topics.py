""" Список mqtt топиков для каждого модуля. Стандарт: mqtt_topics_<название модуля> """

list_of_mqtt_topics = [ ("/devices/HeaterModule/controls/MEAS DAC Vout", 0),
                        ("/devices/HeaterModule/controls/MEAS SW REG Vout", 0),
                        ("/devices/HeaterModule/controls/MEAS LDO REG Vout", 0),
                        ("/devices/HeaterModule/controls/MEAS Load Current", 0),
                        ("/devices/HeaterModule/controls/MEAS REG Vdelta", 0),
                        ("/devices/HeaterModule/controls/OverCrrent Status", 0),
                        ("/devices/HeaterModule/controls/Output Voltage State", 0),
                        ("/devices/MeasureModule/controls/CH1 Voltage", 0),
                        ("/devices/MeasureModule/controls/CH2 Voltage", 0),
                        ("/devices/MeasureModule/controls/CH1 Resistance", 0),
                        ("/devices/MeasureModule/controls/CH2 Resistance", 0),
                        ("/devices/FilteredValues/controls/CH1 Current", 0),
                        ("/devices/FilteredValues/controls/CH1 Temperature", 0),
                        ("/devices/FilteredValues/controls/CH2 Temperature", 0),
                        ("/devices/FilteredValues/controls/CH2 Current", 0),
                        ("/devices/FilteredValues/controls/LDO Power", 0),
                        ("/devices/FilteredValues/controls/LDO Voltage", 0),
                        ("/devices/MeasureModuleSetpoints/controls/CH1 State", 0),
                        ("/devices/MeasureModuleSetpoints/controls/CH2 State", 0)
                                 ]
#Топики для пид модуля
mqtt_topics_pid = {
    "input_value": "/devices/FilteredValues/controls/CH1 Temperature", #Входное значение для ПИД'a (float)
    "output_value" : "/devices/HeaterModule/controls/LDO Counts Set/on", #Выходное значение от ПИД'a (int)
    "input_setpoint_value" : "/devices/MeasureModuleSetpoints/controls/CH1 Temperature Setpoint", #Входное значение уставки для ПИД'a (float)
    "input_pid_current" : "", #Установить текущее напряжение для ПИД'a (int)
    "input_state" : "/devices/HeaterModule/controls/Output Voltage State/on", #Включить/Выключить ПИД регуляцию (0/1)
    "output_state" : "/devices/HeaterModule/controls/Output Voltage State/on",#Включить/Выключить ПИД регуляцию (0/1)
    "input_PID_values_P_value" : "/devices/MeasureModuleSetpoints/PID Kp",#Коэффициент P (float)
    "input_PID_values_I_value" : "/devices/MeasureModuleSetpoints/PID Ki",#Коэффициент I (float)
    "input_PID_values_D_value" : "/devices/MeasureModuleSetpoints/PID Kd",#Коэффициент D (float)
    
    # Ключ: название
    # Значение: топик модуля, котрый будет отвечать за смену
    # topic_value значения будет содержать название топика, на который надо сменить
    "change_topic_input_value" : "/devices/ChangerModule/Change input",
    "change_topic_output_value" : "/devices/ChangerModule/Change output",
    "change_topic_input_setpoint_value" : "/devices/ChangerModule/Change input",
    "change_topic_input_state" : "/devices/HeaterModule/controls/Output Voltage State/Change input", 
    "change_topic_output_state" : "/devices/HeaterModule/controls/Output Voltage State/Change output", 
    "change_topic_input_PID_value_P_value" : "/devices/ChangerModule/Change input",
    "change_topic_input_PID_values_I_value" : "/devices/ChangerModule/Change input", 
    "change_topic_input_PID_values_D_value" : "/devices/ChangerModule/Change input" 
}

mqtt_topics_system_module = {
    "input_wifi_state": "/a/b/c/wifi_state", #Вкл/Выкл вай фай модуль (0/1)
    "input_wifi_mode" : "/a/b/c/wifi_mode", #Режим работы вай фай модуля (client/hotspot)
    "input_wifi_client_ssid" : "/a/b/c/wifi_client_ssid", #Имя сети для режима клиента (any)
    "input_wifi_client_password" : "/a/b/c/wifi_client_password", #Пароль сетя для режима клиента (any)
    "input_wifi_hotspot_ssid" : "/a/b/c/wifi_hotspot_ssid", #Имя сети для режима хотспот'a (any)
    "input_wifi_hotspot_password" : "/a/b/c/wifi_hotspot_password", #Пароль сетя для режима хотспот'a (any)
    "input_eth_mode" : "/a/b/c/eth_mode", #Режим ethernet соединения (static/dhcp)
    "input_eth_ip" : "/a/b/c/eth_ip", #Ip для ethernet соединения (any)
    "input_eth_mask" : "/a/b/c/eth_mask", #Маска сети для ethernet соединения (any)
    "input_eth_gateway" : "/a/b/c/eth_gateway", #Шлюз для ethernet соединения (any)
    "input_update_files_list" : "/a/b/c/update_files_list", #Обновить список файлов в системе (None)
    "output_update_files_list" : "/a/b/c/update_files_list" #Отправить список файлов из системы на дисплей(None)
}
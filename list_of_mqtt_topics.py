""" Список mqtt топиков для каждого модуля. Стандарт: mqtt_topics_<название модуля> """

list_of_mqtt_topics = [ ("/devices/HeaterModule/controls/Output Voltage State", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH1 ConfigFname", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH1 FilterBufferSize", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH1 FilterType", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH1 Heater FilterBufferSize", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH1 Heater FilterType", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH1 SensorModel", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH2 ConfigFname", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH2 FilterBufferSize", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH2 FilterType", 0),
                        ("/devices/MeasureModuleConfigs/controls/CH2 SensorModel", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH1 Heater LDO Current", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH1 Heater LDO Power", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH1 Heater LDO Voltage", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH1 MeasureModule Current", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH1 MeasureModule State", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH1 MeasureModule Temperature", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH2 MeasureModule Current", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH2 MeasureModule State", 0),
                        ("/devices/MeasureModuleOutputs/controls/CH2 MeasureModule Temperature", 0),
                        ("/devices/PIDControl/controls/CH1 Heater PID Kd", 0),
                        ("/devices/PIDControl/controls/CH1 Heater PID Kp", 0),
                        ("/devices/PIDControl/controls/CH1 Heater PID Ki", 0),
                        ("/devices/PIDControl/controls/CH1 Heater PID Status", 0),
                        ("/devices/PIDControl/controls/CH1 Heater Temperaure Setpoint", 0),
                        ("/devices/PIDControl/controls/CH1 Heater Voltage MAX Limit", 0),
                        ("/devices/PIDControl/controls/CH1 MeasureModule Current Setpoint", 0),
                        ("/devices/PIDControl/controls/CH2 MeasureModule Current Setpoint", 0),
                        ("/devices/network/controls/Ethernet 2 IP", 0),
                        ("/devices/network/controls/Wi-Fi IP", 0),
                        ("/devices/SystemModule/controls/Config Files List", 0),
                        ("/devices/SystemModule/controls/Rescaled Temp1", 0),
                        ("/devices/SystemModule/controls/Rescaled Temp2", 0),
                                 ]

#Топики для пид модуля на нагреватель
mqtt_topics_heater_pid = {
    "input_value": "/devices/MeasureModuleOutputs/controls/CH1 MeasureModule Temperature", #Входное значение для ПИД'a (float)
    "output_value" : "/devices/HeaterModule/controls/LDO Counts Set/on", #Выходное значение от ПИД'a (int)
    "input_setpoint_value" : "/devices/PIDControl/controls/CH1 Heater Temperaure Setpoint", #Входное значение уставки для ПИД'a (float)
    "input_pid_current" : "/devices/PIDControl/controls/CH1 Heater Voltage MAX Limit", #Установить текущее напряжение для ПИД'a (int)
    "input_state" : "/devices/HeaterModule/controls/Output Voltage State/on", #Включить/Выключить ПИД регуляцию (0/1)
    "output_state" : "/devices/HeaterModule/controls/Output Voltage State/on",#Включить/Выключить ПИД регуляцию (0/1)
    "output_state_str" : "/devices/PIDControl/controls/CH1 Heater PID Status/on", #Состояние в текстовом формате
    "output_state_num" : "/devices/PIDControl/controls/CH1 Heater PID StatusCode/on", #Состояние в текстовом формате
    "input_PID_values_P_value" : "/devices/PIDControl/controls/CH1 Heater PID Kp",#Коэффициент P (float)
    "input_PID_values_I_value" : "/devices/PIDControl/controls/CH1 Heater PID Ki",#Коэффициент I (float)
    "input_PID_values_D_value" : "/devices/PIDControl/controls/CH1 Heater PID Kd",#Коэффициент D (float)
    
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

#Топики для пид модуля на датчик канала 1
mqtt_topics_current_ch1_pid = {
    "input_value": "/devices/MeasureModuleOutputs/controls/CH1 MeasureModule Current", #Входное значение для ПИД'a (float)
    "output_value" : "/devices/MeasureModule/controls/CH1 DAC/on", #Выходное значение от ПИД'a (int)
    "input_setpoint_value" : "/devices/PIDControl/controls/CH1 MeasureModule Current Setpoint", #Входное значение уставки для ПИД'a (float)
    "input_pid_current" : "/devices/PIDControl/controls/CH1 MeasureModule Current MAX Limit", #Установить текущее напряжение для ПИД'a (int)
    "input_state" : "/devices/PIDControl/controls/CH1 MeasureModule PID State", #Включить/Выключить ПИД регуляцию (0/1)
    "output_state" : "/devices/PIDControl/controls/CH1 MeasureModule PID State/on",#Включить/Выключить ПИД регуляцию (0/1)
    "output_state_str" : "/a/b/c/on", #Состояние в текстовом формате
    "input_PID_values_P_value" : "/devices/PIDControl/controls/CH1 MeasureModule PID Kp",#Коэффициент P (float)
    "input_PID_values_I_value" : "/devices/PIDControl/controls/CH1 MeasureModule PID Ki",#Коэффициент I (float)
    "input_PID_values_D_value" : "/devices/PIDControl/controls/CH1 MeasureModule PID Kd",#Коэффициент D (float)
    
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

#Топики для пид модуля на датчик канала 2
mqtt_topics_current_ch2_pid = {
    "input_value": "/devices/MeasureModuleOutputs/controls/CH2 MeasureModule Current", #Входное значение для ПИД'a (float)
    "output_value" : "/devices/MeasureModule/controls/CH2 DAC/on", #Выходное значение от ПИД'a (int)
    "input_setpoint_value" : "/devices/PIDControl/controls/CH2 MeasureModule Current Setpoint", #Входное значение уставки для ПИД'a (float)
    "input_pid_current" : "/devices/PIDControl/controls/CH2 MeasureModule Current MAX Limit", #Установить текущее напряжение для ПИД'a (int)
    "input_state" : "/devices/PIDControl/controls/CH2 MeasureModule PID State", #Включить/Выключить ПИД регуляцию (0/1)
    "output_state" : "/devices/PIDControl/controls/CH2 MeasureModule PID State/on",#Включить/Выключить ПИД регуляцию (0/1)
    "output_state_str" : "/a/b/d/on", #Состояние в текстовом формате
    "input_PID_values_P_value" : "/devices/PIDControl/controls/CH2 MeasureModule PID Kp",#Коэффициент P (float)
    "input_PID_values_I_value" : "/devices/PIDControl/controls/CH2 MeasureModule PID Ki",#Коэффициент I (float)
    "input_PID_values_D_value" : "/devices/PIDControl/controls/CH2 MeasureModule PID Kd",#Коэффициент D (float)
    
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
    "input_wifi_state": "/devices/SystemModule/controls/WiFi State", #Вкл/Выкл вай фай модуль (0/1)
    "input_wifi_mode" : "/devices/SystemModule/controls/WiFi Mode", #Режим работы вай фай модуля (client/hotspot)
    "input_wifi_client_ssid" : "/devices/SystemModule/controls/WiFi Client SSID", #Имя сети для режима клиента (any)
    "input_wifi_client_password" : "/devices/SystemModule/controls/WiFi Client Password", #Пароль сетя для режима клиента (any)
    "input_wifi_hotspot_ssid" : "/devices/SystemModule/controls/WiFi Hotspot SSID", #Имя сети для режима хотспот'a (any)
    "input_wifi_hotspot_password" : "/devices/SystemModule/controls/WiFi Hotspot Password", #Пароль сетя для режима хотспот'a (any)
    "input_eth_mode" : "/devices/SystemModule/controls/ETH0 Mode", #Режим ethernet соединения (static/dhcp)
    "input_eth_ip" : "/devices/SystemModule/controls/ETH0 IP", #Ip для ethernet соединения (any)
    "input_eth_mask" : "/devices/SystemModule/controls/ETH0 Mask", #Маска сети для ethernet соединения (any)
    "input_eth_gateway" : "/a/b/c/eth_gateway", #Шлюз для ethernet соединения (any)
    "input_update_files_list" : "/devices/SystemModule/controls/Update Config Files Event", #Обновить список файлов в системе (None)
    "input_temperature1": "/devices/MeasureModuleOutputs/controls/CH1 MeasureModule Temperature",
    "input_temperature2": "/devices/MeasureModuleOutputs/controls/CH2 MeasureModule Temperature",
    "output_update_files_list" : "/devices/SystemModule/controls/Config Files List" #Отправить список файлов из системы на дисплей(None)
}


mqtt_topics_plotter_module = {
    "input_user_scale_min": "/devices/SystemModule/controls/User Scale Min",
    "input_user_scale_max": "/devices/SystemModule/controls/User Scale Max",
    "output_rescaled_temp1" : "/devices/SystemModule/controls/Rescaled Temp1", #
    "output_rescaled_temp2" : "/devices/SystemModule/controls/Rescaled Temp2" #
}

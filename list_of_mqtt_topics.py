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

mqtt_topics_pid = {
    "input_value": "/devices/FilteredValues/controls/CH1 Temperature",
    "output_value" : "/devices/HeaterModule/controls/LDO Counts Set/on",
    "input_setpoint_value" : "/devices/MeasureModuleSetpoints/controls/CH1 Temperature Setpoint",
    "input_state" : "/devices/HeaterModule/controls/Output Voltage State/on",
    "output_state" : "/devices/HeaterModule/controls/Output Voltage State/on",
    "input_PID_values_P_value" : "/devices/MeasureModuleSetpoints/PID Kp",
    "input_PID_values_I_value" : "/devices/MeasureModuleSetpoints/PID Ki",
    "input_PID_values_D_value" : "/devices/MeasureModuleSetpoints/PID Kd",
    
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
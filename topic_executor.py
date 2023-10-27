import general_functions

class TopicExecutor:
    
    def __init__(self, nextion_mqtt_bridge, group_name, module_name, topic_val):
        self.nextion_mqtt_bridge = nextion_mqtt_bridge
        self.group_name = group_name
        self.module_name = module_name
        self.topic_val = topic_val
        

     
    


    """  heater_module """
    
    
    def MEAS_Load_Current(self):
        load_current = round(float(self.topic_val), 3)
        self.nextion_mqtt_bridge.ldo_current_value = load_current
        cmd = 'mesurments.t14.txt="' + str(load_current) + '"'
        self.nextion_mqtt_bridge.serial_write(cmd)
        self.nextion_mqtt_bridge.calculate_ldo_power(self.nextion_mqtt_bridge.ldo_voltage_value, self.nextion_mqtt_bridge.ldo_current_value, self.nextion_mqtt_bridge.ldo_power_topic)

    def Output_Voltage_State(self):
        if self.topic_val == "1":
            for cmd in general_functions.heater_on_cmds:
                self.nextion_mqtt_bridge.serial_write(cmd)
        elif self.topic_val == "0":
            for cmd in general_functions.heater_off_cmds:
                self.nextion_mqtt_bridge.serial_write(cmd)
    
    heater_module = {
        'MEAS Load Current' : MEAS_Load_Current,
        'Output Voltage State' : Output_Voltage_State,
    }   
    
    
    
    
    
    
    
    
    
    
    """  measure_module """
    

    def CH1_Resistance(self):
        raw_temp = general_functions.convert_resistanc_to_temp(float(self.topic_val))
        self.nextion_mqtt_bridge.ch1_temp_list.append(raw_temp[1])
        if len(self.nextion_mqtt_bridge.ch1_temp_list) == self.nextion_mqtt_bridge.aver_buff_size:
            general_functions.calculate_moving_average(self.nextion_mqtt_bridge.ch1_temp_list, self.nextion_mqtt_bridge.aver_buff_size, self.nextion_mqtt_bridge.broker, self.nextion_mqtt_bridge.ch1_fitered_temp_topic)
            self.nextion_mqtt_bridge.ch1_temp_list = list()

    def CH2_Resistance(self):
        raw_temp = general_functions.convert_resistanc_to_temp(float(self.opic_val))
        self.nextion_mqtt_bridge.ch2_temp_list.append(raw_temp[1])
        if len(self.nextion_mqtt_bridge.ch2_temp_list) == self.nextion_mqtt_bridge.aver_buff_size:
            general_functions.calculate_moving_average(self.nextion_mqtt_bridge.ch2_temp_list, self.nextion_mqtt_bridge.aver_buff_size, self.nextion_mqtt_bridge.broker, self.nextion_mqtt_bridge.ch2_fitered_temp_topic)
            self.nextion_mqtt_bridge.ch2_temp_list = list()

    measure_module = {
        'CH1 Resistance': CH1_Resistance,
        'CH2 Resistance': CH2_Resistance,
    }
    
    
    
    
    
    
    
    
    
    """filtered_values"""
    
    
    def CH1_Current(self):
        current = round(float(self.topic_val), 3)
        cmd = 'mesurments.t6.txt="' + str(current) + '"'
        self.nextion_mqtt_bridge.serial_write(cmd)

    def CH2_Current(self):
        current = round(float(self.topic_val), 3)
        cmd = 'mesurments.t8.txt="' + str(current) + '"'
        self.nextion_mqtt_bridge.serial_write(cmd)
        
    def LDO_Voltage(self):
        load_voltage = round(float(self.topic_val), 3)
        self.nextion_mqtt_bridge.ldo_voltage_value = load_voltage
        cmd = 'mesurments.t12.txt="' + str(load_voltage) + '"'
        self.nextion_mqtt_bridge.serial_write(cmd)
        self.nextion_mqtt_bridge.calculate_ldo_power(self.nextion_mqtt_bridge.ldo_voltage_value, self.nextion_mqtt_bridge.ldo_current_value, self.nextion_mqtt_bridge.ldo_power_topic)
        
    def CH1_Temperature(self):
        ch1_temp = round(float(self.topic_val), 2)
        cmd = 'mesurments.t0.txt="' + str(ch1_temp) + '"'
        self.nextion_mqtt_bridge.serial_write(cmd)
        
    def CH2_Temperature(self):
        ch2_temp = round(float(self.topic_val), 2)
        cmd = 'mesurments.t2.txt="' + str(ch2_temp) + '"'
        self.nextion_mqtt_bridge.serial_write(cmd)
        
    def LDO_Power(self):
        power = round(float(self.topic_val), 2)
        cmd = 'mesurments.t16.txt="' + str(power) + '"'
        self.nextion_mqtt_bridge.serial_write(cmd)
            
    filtered_values = {
        
        'CH1 Current' : CH1_Current,
        'CH2 Current' : CH2_Current,
        'LDO Voltage' : LDO_Voltage,
        'CH1 Temperature' : CH1_Temperature,
        'CH2 Temperature' : CH2_Temperature,
        'LDO Power' : LDO_Power,
        
        }
    
    
    
    
    
    
    
    """measure_module_setpoints"""
    
    
    def CH1_State(self):
        if self.topic_val == "1":
            for cmd in general_functions.ch1_current_on_cmds:
                self.nextion_mqtt_bridge.serial_write(cmd)
        elif self.topic_val == "0":
            for cmd in general_functions.ch1_current_off_cmds:
                self.nextion_mqtt_bridge.serial_write(cmd)
    
    def CH2_State(self):
        if self.topic_val == "1":
            for cmd in general_functions.ch2_current_on_cmds:
                self.nextion_mqtt_bridge.serial_write(cmd)
        elif self.topic_val == "0":
            for cmd in general_functions.ch2_current_off_cmds:
                self.nextion_mqtt_bridge.serial_write(cmd)
                    
    measure_module_setpoints = {

        'CH1 State' : CH1_State,
        'CH2 State' : CH2_State
        
        }







    """group_names"""

    group_names = {
        
        'HeaterModule' : heater_module,
        'MeasureModule': measure_module,
        'FilteredValues' : filtered_values,
        'MeasureModuleSetpoints' : measure_module_setpoints
        
        }
    

    def execute(self):
        try:
            self.group_names[self.group_name][self.module_name](self)
        except KeyError as key_error:
            raise KeyError('Ключ не найден (функция для данного топика не прописана)')
            



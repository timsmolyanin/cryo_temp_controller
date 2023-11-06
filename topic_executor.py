class TopicExecutor:
    
    def __init__(self, nextion_mqtt_bridge, group_name, module_name, topic_value, config):
        self.nextion_mqtt_bridge = nextion_mqtt_bridge
        self.group_name = group_name
        self.module_name = module_name
        self.topic_value = topic_value
        self.config = config
    
    def execute(self):
        try:
            module = self.config[self.group_name][self.module_name]
        except KeyError as key_error:
            raise key_error('Ключ не найден, топик не прописан')
        
        if module['Condition'] == 'False':
            cmd = module['Cmd'] + self.topic_value
            print(cmd)
            self.nextion_mqtt_bridge.serial_write(cmd)
            return
            
            
        if module['Condition'] == 'True':
            try:
                cmds = module[str(self.topic_value)]
            except KeyError:
                raise KeyError('Состояния "' + str(self.topic_value) + '" в модуле "' + self.module_name + '" не существует. Группа: "' + self.group_name + '"')
            
            for cmd in cmds:
                self.nextion_mqtt_bridge.serial_write(cmd)
                print(cmd)
            return
        
    
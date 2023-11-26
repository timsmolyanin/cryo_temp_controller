

import system_module
import pid_control

mqtt_broker = "192.168.44.11"
mqtt_port = 1883
mqtt_user = "admin"
mqtt_password = "admin"

sys_module = system_module.SystemModule(mqtt_broker, mqtt_port, mqtt_user, mqtt_password)
sys_module.start()

pid_module = pid_control.PIDControl(mqtt_broker, mqtt_port, mqtt_user, mqtt_password)
pid_module.set_pid_limits_min(0)
pid_module.set_pid_limits_max(50)
pid_module.start()
defineVirtualDevice("PIDControl", {
    title: "PIDControl",
    cells: {
      "CH1 Heater Temperaure Setpoint": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 Heater Voltage MAX Limit": {
      type: "value",
      value: 5.0,
      readonly: false
      },
      "CH1 Heater PID Kp": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 Heater PID Kd": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 Heater PID Ki": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 Heater PID Status": {
      type: "text",
      value: "Unknown",
      readonly: false
      },
      "CH1 Heater PID StatusCode": {
      type: "text",
      value: "0",
      readonly: false
      },
      "CH1 Heater SensorTopic": {
      type: "text",
      value: "/devices/MeasureModuleOutputs/controls/CH1 MeasureModule Temperature",
      readonly: false
      },
      "CH1 MeasureModule Current Setpoint": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 MeasureModule Current MAX Limit": {
      type: "value",
      value: 500,
      readonly: false
      },
      "CH1 MeasureModule PID State": {
      type: "value",
      value: 0,
      readonly: false
      },
      "CH1 MeasureModule PID Kp": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 MeasureModule PID Kd": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 MeasureModule PID Ki": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 MeasureModule PID Status": {
      type: "text",
      value: "Unknown",
      readonly: false
      },
      "CH2 MeasureModule Current Setpoint": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH2 MeasureModule Current MAX Limit": {
      type: "value",
      value: 500,
      readonly: false
      },
      "CH2 MeasureModule PID State": {
      type: "value",
      value: 0,
      readonly: false
      },
      "CH2 MeasureModule PID Kp": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH2 MeasureModule PID Kd": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH2 MeasureModule PID Ki": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH2 MeasureModule PID Status": {
      type: "text",
      value: "Unknown",
      readonly: false
      }
    }
  });
  
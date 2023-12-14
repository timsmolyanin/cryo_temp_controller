defineVirtualDevice("MeasureModuleConfigs", {
    title: "MeasureModuleConfigs",
    cells: {
      "CH1 Heater FilterType": {
      type: "text",
      value: "Median",
      readonly: false
      },
      "CH1 Heater FilterBufferSize": {
      type: "value",
      value: 10,
      readonly: false
      },
      "CH1 FilterType": {
      type: "text",
      value: "Median",
      readonly: false
      },
      "CH2 FilterType": {
      type: "text",
      value: "Median",
      readonly: false
      },
      "CH1 FilterBufferSize": {
      type: "value",
      value: 10,
      readonly: false
      },
      "CH2 FilterBufferSize": {
      type: "value",
      value: 10,
      readonly: false
      },
      "CH1 SensorModel": {
      type: "text",
      value: "Diode",
      readonly: false
      },
      "CH2 SensorModel": {
      type: "text",
      value: "Pt1000",
      readonly: false
      },
      "CH1 ConfigFname": {
      type: "text",
      value: "CDA005.340",
      readonly: false
      },
      "CH2 ConfigFname": {
      type: "text",
      value: "pt1000_config_2.txt",
      readonly: false
      },
    }
  });
defineVirtualDevice("MeasureModuleOutputs", {
    title: "MeasureModuleOutputs",
    cells: {
      "CH1 MeasureModule Current": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH2 MeasureModule Current": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 MeasureModule Temperature": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH2 MeasureModule Temperature": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 MeasureModule State": {
      type: "text",
      value: "Unknown",
      readonly: false
      },
      "CH2 MeasureModule State": {
      type: "text",
      value: "Unknown",
      readonly: false
      },
      "CH1 Heater LDO Voltage": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 Heater LDO Current": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "CH1 Heater LDO Power": {
      type: "value",
      value: 0.0,
      readonly: false
      }
    }
  });
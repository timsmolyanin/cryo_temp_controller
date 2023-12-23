defineVirtualDevice("SystemModule", {
    title: "SystemModule",
    cells: {
      "WiFi State": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "WiFi Mode": {
      type: "text",
      value: "hotspot",
      readonly: false
      },
      "WiFi Hotspot SSID": {
      type: "text",
      value: "TempCryoController",
      readonly: false
      },
      "WiFi Hotspot Password": {
      type: "text",
      value: "qwerty12345",
      readonly: false
      },
      "WiFi Client SSID": {
      type: "text",
      value: "",
      readonly: false
      },
      "WiFi Client Password": {
      type: "text",
      value: "",
      readonly: false
      },
      "ETH0 Mode": {
      type: "text",
      value: "static",
      readonly: false
      },
      "ETH0 IP": {
      type: "text",
      value: "192.168.44.10",
      readonly: false
      },
      "ETH0 Mask": {
      type: "text",
      value: "255.255.255.0",
      readonly: false
      },
      "Update Config Files Event": {
      type: "value",
      value: 0.0,
      readonly: false
      },
      "Config Files List": {
      type: "text",
      value: "",
      readonly: false
      },
      "User Scale Min": {
        type: "value",
        value: "",
        readonly: false
      },
      "User Scale Max": {
        type: "value",
        value: "",
        readonly: false
      },
      "Rescaled Temp1": {
        type: "value",
        value: "",
        readonly: false
      },
      "Rescaled Temp2": {
        type: "value",
        value: "",
        readonly: false
      }
    }
  });
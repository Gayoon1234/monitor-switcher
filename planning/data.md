Display
├── id
├── name
└── inputs
x ├── input_id
x └── input_type - ANALOG, HDMI, etc

USB Device
x ├── id
x ├── windows_device_id
x └── name

Automation
x ├── id
x ├── name
x ├── enabled - boolean
x ├── trigger
xxx ├── type - enum - device connected/disconnected
xxx └── device_id
x └── actions - list
xxx ├── type - enum - switch/do_nothing
xxx ├── display_id
xxx └── input_id

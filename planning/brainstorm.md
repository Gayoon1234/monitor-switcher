## Decisions/Brainstorm

- PySide6 for UI framework
- Custom styles
- UI should talk to service layer which abstracts it
- UI -> Services -> Hardware
- we can take advantage of dataclasses first - look at databases later
- same with config/save state, put it on json first - segregate from installer.
- create interfaces for monitor control/wmi
- event driven architecture

## Features

- My Devices: Two panels, one for displays, one for usb periperals, "Add/remove options"
- Find My Device: Finds Windows Hardware device is by plugging it in. Allows setting nickname, also applicable to monitors.
- Automations: When "x" connects, send "y" to display "z", "when if do model"
- Logs: Automation triggered etc

Device Ids are not intuitive so we will add nicknames to be used on the My Devices and Automations pages.

Modern, dark/light capable desktop utility — closer to a polished Windows settings app than a generic Python GUI.
Themes are important, we should support theming like linux and build some themes that go mroe than light/dark.

Eventbus needs to have a spare wheel

## Stack

pyside6 - UI
monitorcontrol - send signals to monitor
pywin32 - maybe required for windows calls.

## Testing

- Will not be required as I am a perfect programmer who makes no mistakes.

from app.models.display import Display, DisplayInput, InputType
from app.models.usb_device import UsbDevice
from app.models.automation import (
    Automation,
    Trigger,
    TriggerType,
    Action,
    ActionType,
)


philips = Display(
    id="display-001",
    name="Philips",
    inputs=[
        DisplayInput("HDMI1", InputType.HDMI),
        DisplayInput("ANALOG1", InputType.ANALOG),
    ],
)


usb_switch = UsbDevice(
    id="usb-001",
    windows_device_id=r"USB\VID_05E3&PID_0626\5&21296CF&0&17",
    name="Desk USB Switch",
)


switch_to_mac = Automation(
    id="automation-001",
    name="Switch to Mac",
    enabled=True,
    trigger=Trigger(
        type=TriggerType.DEVICE_CONNECTED,
        device_id=usb_switch.id,
    ),
    actions=[
        Action(
            type=ActionType.SWITCH_INPUT,
            display_id=philips.id,
            input_id="ANALOG1",
        ),
    ],
)


print(philips)
print(usb_switch)
print(switch_to_mac)
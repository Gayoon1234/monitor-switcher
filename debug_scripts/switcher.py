import time
import win32com.client

from monitorcontrol import get_monitors, InputSource


HUB_ID = r"USB\VID_05E3&PID_0626\5&21296CF&0&17"

monitor = get_monitors()[0]

wmi = win32com.client.GetObject("winmgmts:")


def hub_connected():
    devices = wmi.ExecQuery(
        "SELECT DeviceID FROM Win32_PnPEntity WHERE PNPClass = 'USB'"
    )

    return any(device.DeviceID == HUB_ID for device in devices)


def set_monitor_input(source):
    with monitor:
        monitor.set_input_source(source)


last_state = hub_connected()

print(f"USB switch: {'PC' if last_state else 'Mac'}")

while True:
    current_state = hub_connected()

    if current_state != last_state:
        if current_state:
            print("USB switch → PC")
            print("Switching monitor → HDMI")
            set_monitor_input(InputSource.HDMI1)
        else:
            print("USB switch → Mac")
            print("Switching monitor → VGA")
            set_monitor_input(InputSource.ANALOG1)

        last_state = current_state

    time.sleep(0.5)
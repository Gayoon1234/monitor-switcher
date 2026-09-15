import time
import win32com.client

from monitorcontrol import get_monitors, InputSource


HUB_ID = r"USB\VID_05E3&PID_0626\5&21296CF&0&17"

monitors = get_monitors()

monitor1 = monitors[0]
monitor2 = monitors[1]

wmi = win32com.client.GetObject("winmgmts:")


def hub_connected():
    devices = wmi.ExecQuery(
        "SELECT DeviceID FROM Win32_PnPEntity WHERE PNPClass = 'USB'"
    )

    return any(device.DeviceID == HUB_ID for device in devices)


def set_pc_inputs():
    print("Switching monitors → PC")

    with monitor1:
        monitor1.set_input_source(InputSource.HDMI1)

    with monitor2:
        monitor2.set_input_source(InputSource.ANALOG1)


def set_mac_inputs():
    print("Switching monitors → Mac")

    with monitor1:
        monitor1.set_input_source(InputSource.ANALOG1)

    with monitor2:
        monitor2.set_input_source(InputSource.DVI1)


last_state = hub_connected()

print(f"USB switch: {'PC' if last_state else 'Mac'}")
print("Watching for USB switch changes...")
print("Press Ctrl+C to stop.")


try:
    while True:
        current_state = hub_connected()

        if current_state != last_state:
            if current_state:
                set_pc_inputs()
            else:
                set_mac_inputs()

            last_state = current_state

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopped.")
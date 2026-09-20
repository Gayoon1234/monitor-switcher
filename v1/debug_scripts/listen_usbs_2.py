import time
import win32com.client

wmi = win32com.client.GetObject("winmgmts:")

def get_usb_devices():
    devices = wmi.ExecQuery(
        "SELECT DeviceID, Name, PNPClass FROM Win32_PnPEntity "
        "WHERE PNPClass = 'USB'"
    )

    return {
        device.DeviceID: device.Name
        for device in devices
        if device.DeviceID
    }


previous = get_usb_devices()

print("Watching USB devices...")
print("Switch the USB switch and watch what appears/disappears.\n")

while True:
    time.sleep(1)

    current = get_usb_devices()

    connected = current.keys() - previous.keys()
    disconnected = previous.keys() - current.keys()

    for device_id in disconnected:
        print(f"DISCONNECTED: {previous[device_id]}")
        print(f"  {device_id}\n")

    for device_id in connected:
        print(f"CONNECTED: {current[device_id]}")
        print(f"  {device_id}\n")

    previous = current
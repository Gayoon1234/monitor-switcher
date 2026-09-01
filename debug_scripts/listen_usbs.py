import time
import win32com.client

wmi = win32com.client.GetObject("winmgmts:")

watchers = [
    wmi.ExecNotificationQuery(
        "SELECT * FROM Win32_DeviceChangeEvent WHERE EventType = 2"
    ),
    wmi.ExecNotificationQuery(
        "SELECT * FROM Win32_DeviceChangeEvent WHERE EventType = 3"
    ),
]

print("Watching for USB/device changes...")
print("Switch your USB switch and watch the output.\n")

while True:
    for watcher in watchers:
        try:
            event = watcher.NextEvent(100)
            event_type = event.EventType

            if event_type == 2:
                print("DEVICE CONNECTED")
            elif event_type == 3:
                print("DEVICE DISCONNECTED")

            print(f"  EventType: {event_type}\n")

        except Exception:
            pass

    time.sleep(0.1)
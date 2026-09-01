import threading
import time

import pythoncom
import pystray
import win32com.client

from PIL import Image, ImageDraw
from monitorcontrol import get_monitors, InputSource


HUB_ID = r"USB\VID_05E3&PID_0626\5&21296CF&0&17"


# ----------------------------
# State
# ----------------------------

current_state = None
state_lock = threading.Lock()

tray_icon = None
stop_event = threading.Event()


# ----------------------------
# Tray icon
# ----------------------------

def create_icon():
    image = Image.new("RGB", (64, 64), "white")

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (8, 8, 56, 44),
        outline="black",
        width=4
    )

    draw.line(
        (24, 52, 40, 52),
        fill="black",
        width=4
    )

    draw.line(
        (32, 44, 32, 52),
        fill="black",
        width=4
    )

    return image


def update_tray():
    if tray_icon is None:
        return

    with state_lock:
        state = current_state

    mode = "PC" if state else "Mac"

    tray_icon.title = f"Monitor Switcher — {mode}"


def get_status_text(item):
    with state_lock:
        state = current_state

    return f"Status: {'PC' if state else 'Mac'}"


def exit_app(icon, item):
    stop_event.set()
    icon.stop()


def create_menu():
    return pystray.Menu(
        pystray.MenuItem(
            get_status_text,
            None,
            enabled=False
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "Exit",
            exit_app
        )
    )


# ----------------------------
# Monitor switching
# ----------------------------

def set_pc_inputs(monitor1, monitor2):
    print("Switching monitors → PC")

    with monitor1:
        monitor1.set_input_source(InputSource.HDMI1)

    with monitor2:
        monitor2.set_input_source(InputSource.ANALOG1)


def set_mac_inputs(monitor1, monitor2):
    print("Switching monitors → Mac")

    with monitor1:
        monitor1.set_input_source(InputSource.ANALOG1)

    with monitor2:
        monitor2.set_input_source(InputSource.DVI1)


# ----------------------------
# USB watcher
# ----------------------------

def watch_usb():
    global current_state

    # COM must be initialized in this thread
    pythoncom.CoInitialize()

    try:
        # Create WMI connection inside this thread
        wmi = win32com.client.GetObject("winmgmts:")

        # Create monitor objects inside this thread
        monitors = get_monitors()

        monitor1 = monitors[0]
        monitor2 = monitors[1]

        def hub_connected():
            devices = wmi.ExecQuery(
                "SELECT DeviceID FROM Win32_PnPEntity "
                "WHERE PNPClass = 'USB'"
            )

            return any(
                device.DeviceID == HUB_ID
                for device in devices
            )

        # Get initial state
        last_state = hub_connected()

        with state_lock:
            current_state = last_state

        print(
            f"USB switch: {'PC' if last_state else 'Mac'}"
        )

        update_tray()

        # Watch for changes
        while not stop_event.is_set():

            current_state_detected = hub_connected()

            if current_state_detected != last_state:

                # Give Windows time to finish
                # the USB transition
                time.sleep(0.25)

                current_state_detected = hub_connected()

                if current_state_detected != last_state:

                    # Debounce
                    time.sleep(0.5)

                    current_state_detected = hub_connected()

                    if current_state_detected != last_state:

                        if current_state_detected:
                            print("\nUSB switch → PC")

                            set_pc_inputs(
                                monitor1,
                                monitor2
                            )

                        else:
                            print("\nUSB switch → Mac")

                            set_mac_inputs(
                                monitor1,
                                monitor2
                            )

                        last_state = current_state_detected

                        with state_lock:
                            current_state = last_state

                        update_tray()

            time.sleep(0.5)

    finally:
        pythoncom.CoUninitialize()


# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":

    tray_icon = pystray.Icon(
        "MonitorSwitcher",
        create_icon(),
        "Monitor Switcher",
        create_menu()
    )

    watcher_thread = threading.Thread(
        target=watch_usb,
        daemon=True
    )

    watcher_thread.start()

    tray_icon.run()
import threading
import time
from typing import Optional

import pythoncom
import pystray
import win32com.client

from PIL import Image, ImageDraw
from monitorcontrol import get_monitors, InputSource


HUB_ID = r"USB\VID_05E3&PID_0626\5&21296CF&0&17"

POLL_INTERVAL_SEC = 0.5
DEBOUNCE_CONFIRM_SEC = 0.25
DEBOUNCE_SETTLE_SEC = 0.5


# ----------------------------
# State
# ----------------------------

current_state: Optional[bool] = None
state_lock = threading.Lock()

tray_icon: Optional[pystray.Icon] = None
stop_event = threading.Event()


# ----------------------------
# Helpers
# ----------------------------

def mode_name(hub_connected: bool) -> str:
    return "PC" if hub_connected else "Mac"


def hub_connected(wmi) -> bool:
    devices = wmi.ExecQuery(
        "SELECT DeviceID FROM Win32_PnPEntity "
        "WHERE PNPClass = 'USB'"
    )

    return any(device.DeviceID == HUB_ID for device in devices)


def confirm_state_change(wmi, last_state: bool) -> Optional[bool]:
    """Re-check hub state after debounce delays; return new state or None."""
    time.sleep(DEBOUNCE_CONFIRM_SEC)
    if hub_connected(wmi) == last_state:
        return None

    time.sleep(DEBOUNCE_SETTLE_SEC)
    new_state = hub_connected(wmi)
    if new_state == last_state:
        return None

    return new_state


# ----------------------------
# Tray icon
# ----------------------------

def create_icon():
    image = Image.new("RGB", (64, 64), "white")
    draw = ImageDraw.Draw(image)

    draw.rectangle((8, 8, 56, 44), outline="black", width=4)
    draw.line((24, 52, 40, 52), fill="black", width=4)
    draw.line((32, 44, 32, 52), fill="black", width=4)

    return image


def update_tray():
    if tray_icon is None:
        return

    with state_lock:
        state = current_state

    tray_icon.title = f"Monitor Switcher — {mode_name(state)}"


def get_status_text(_item):
    with state_lock:
        state = current_state

    return f"Status: {mode_name(state)}"


def exit_app(icon, _item):
    stop_event.set()
    icon.stop()


def create_menu():
    return pystray.Menu(
        pystray.MenuItem(get_status_text, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", exit_app),
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


def apply_input_switch(is_pc: bool, monitor1, monitor2) -> None:
    try:
        if is_pc:
            set_pc_inputs(monitor1, monitor2)
        else:
            set_mac_inputs(monitor1, monitor2)
    except Exception as exc:
        print(f"Failed to switch monitors: {exc}")


# ----------------------------
# USB watcher
# ----------------------------

def watch_usb():
    global current_state

    pythoncom.CoInitialize()

    try:
        wmi = win32com.client.GetObject("winmgmts:")
        monitors = get_monitors()

        if len(monitors) < 2:
            print(f"Expected at least 2 monitors, found {len(monitors)}")
            return

        monitor1 = monitors[0]
        monitor2 = monitors[1]

        last_state = hub_connected(wmi)

        with state_lock:
            current_state = last_state

        print(f"USB switch: {mode_name(last_state)}")
        update_tray()

        while not stop_event.is_set():
            if hub_connected(wmi) != last_state:
                new_state = confirm_state_change(wmi, last_state)
                if new_state is not None:
                    print(f"\nUSB switch → {mode_name(new_state)}")
                    apply_input_switch(new_state, monitor1, monitor2)

                    last_state = new_state

                    with state_lock:
                        current_state = last_state

                    update_tray()

            if stop_event.wait(POLL_INTERVAL_SEC):
                break

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
        create_menu(),
    )

    watcher_thread = threading.Thread(target=watch_usb, daemon=True)
    watcher_thread.start()

    tray_icon.run()

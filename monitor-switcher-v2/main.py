from app.hardware.windows_monitor import WindowsMonitorController


controller = WindowsMonitorController()

print("Monitor map:")
for display_id, monitor in controller._monitor_map.items():
    print(f"{display_id}: {monitor}")

print()

print("Discovered displays:")
for display in controller.get_displays():
    print(display)

print()

print("Testing Philips...")
controller.switch_input("display-001", "HDMI1")

print("Done.")
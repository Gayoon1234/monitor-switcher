from monitorcontrol import get_monitors
from monitorcontrol import InputSource

monitor = get_monitors()[0]

with monitor:
    monitor.set_input_source(InputSource.ANALOG1) #ANALOG1 or HDMI1
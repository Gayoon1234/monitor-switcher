from app.models.display import Display, DisplayInput, InputType
from app.models.usb_device import ConfiguredUsbDevice, UsbDevice
from app.ui.widgets.display_card import DisplayCard
from app.ui.widgets.usb_device_card import UsbDeviceCard


class DisplayServiceStub:
    def switch_input(self, display_id, input_id):
        pass


def test_usb_device_cards_show_connection_and_configuration_state(qapp):
    connected_device = UsbDevice(
        windows_device_id="USB\\VID_1234&PID_5678",
        name="USB Hub",
    )
    configured_device = ConfiguredUsbDevice(
        id="device-1",
        windows_device_id=connected_device.windows_device_id,
        nickname="Desk Hub",
    )

    configured_card = UsbDeviceCard(
        connected_device,
        configured_device=configured_device,
        connected=True,
    )
    unconfigured_card = UsbDeviceCard(connected_device)

    assert configured_card.property("deviceState") == "configured"
    assert configured_card.findChild(
        type(configured_card.nickname_label),
        "deviceStatus",
    ).text() == "Connected"
    assert unconfigured_card.property("deviceState") == "unconfigured"


def test_display_card_disables_input_selector_when_no_inputs(qapp):
    display = Display(
        id="display-1",
        name="Main Monitor",
        windows_device_id="DISPLAY\\MONITOR",
        inputs=[],
    )

    card = DisplayCard(display, DisplayServiceStub())

    assert card.objectName() == "displayCard"
    assert not card.input_selector.isEnabled()

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QPushButton, QScrollArea, QSizePolicy

from app.models.display import Display, DisplayInput, InputType
from app.models.usb_device import ConfiguredUsbDevice, UsbDevice
from app.ui.widgets.display_card import DisplayCard
from app.ui.widgets.usb_device_card import UsbDeviceCard
from app.ui.pages.find_my_device import FindMyDevicePage
from app.ui.pages.my_devices import MyDevicesPage


class DisplayServiceStub:
    def switch_input(self, display_id, input_id):
        pass

    def get_displays(self):
        return []


class UsbServiceStub(QObject):
    devices_changed = Signal()

    def __init__(self, devices=None, configured_devices=None):
        super().__init__()
        self.devices = devices or []
        self.configured_devices = configured_devices or []

    def get_devices(self):
        return self.devices

    def get_configured_devices(self):
        return self.configured_devices


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


def test_my_devices_keeps_usb_cards_in_scrollable_content(qapp):
    devices = [
        UsbDevice(f"USB\\DEVICE_{index}", f"Device {index}")
        for index in range(3)
    ]
    configured_devices = [
        ConfiguredUsbDevice(
            str(index),
            device.windows_device_id,
            f"Device {index}",
        )
        for index, device in enumerate(devices)
    ]
    page = MyDevicesPage(
        DisplayServiceStub(),
        UsbServiceStub(devices, configured_devices),
    )

    assert page.device_container.minimumWidth() >= (
        page.device_layout.sizeHint().width()
    )
    assert page.device_scroll_area.widgetResizable() is False


def test_find_device_keeps_usb_cards_in_scrollable_content(qapp):
    devices = [
        UsbDevice(f"USB\\DEVICE_{index}", f"Device {index}")
        for index in range(4)
    ]
    page = FindMyDevicePage(UsbServiceStub(devices))
    scroll_area = page.findChild(QScrollArea)
    container = scroll_area.widget()
    device_layout = container.layout()
    refresh_button = page.findChild(QPushButton, "refreshButton")

    assert scroll_area.widgetResizable() is True
    assert device_layout.columnStretch(0) == 1
    assert device_layout.columnStretch(1) == 1
    assert max(
        device_layout.getItemPosition(index)[1]
        for index in range(device_layout.count())
    ) <= 1
    assert device_layout.itemAt(0).widget().sizePolicy().horizontalPolicy() == (
        QSizePolicy.Policy.Expanding
    )
    assert device_layout.itemAt(0).widget().sizePolicy().verticalPolicy() == (
        QSizePolicy.Policy.Expanding
    )
    assert device_layout.rowStretch(0) == 1
    assert page.content_layout.itemAt(
        page.content_layout.count() - 1
    ).widget() is refresh_button


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

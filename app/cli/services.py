from dataclasses import dataclass

from app.services.activity_repository import ActivityRepository
from app.services.config_repository import ConfigRepository
from app.services.theme_service import ThemeService


@dataclass
class ServiceContext:
    repository: ConfigRepository
    activity_repository: ActivityRepository
    theme_service: ThemeService
    display_service: object | None = None
    usb_service: object | None = None
    automation_service: object | None = None
    usb_monitor: object | None = None

    def close(self) -> None:
        self.activity_repository.close()


def create_context(*, with_hardware: bool = False) -> ServiceContext:
    repository = ConfigRepository()
    activity_repository = ActivityRepository()
    context = ServiceContext(
        repository=repository,
        activity_repository=activity_repository,
        theme_service=ThemeService(),
    )

    if not with_hardware:
        return context

    from app.hardware.windows_monitor import WindowsMonitorController
    from app.hardware.windows_usb import WindowsUsbDeviceMonitor
    from app.services.automation_service import AutomationService
    from app.services.display_service import DisplayService
    from app.services.usb_service import UsbService

    monitor_controller = WindowsMonitorController()
    usb_monitor = WindowsUsbDeviceMonitor()
    display_service = DisplayService(
        monitor_controller=monitor_controller,
        display_discovery=monitor_controller,
        repository=repository,
    )
    usb_service = UsbService(
        device_monitor=usb_monitor,
        repository=repository,
    )

    context.display_service = display_service
    context.usb_service = usb_service
    context.usb_monitor = usb_monitor
    context.automation_service = AutomationService(
        display_service=display_service,
        automations=repository.load_automations(),
        activity_repository=activity_repository,
    )
    return context

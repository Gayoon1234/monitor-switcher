import logging

from PySide6.QtCore import (
    QCoreApplication,
    QObject,
    QRunnable,
    QThreadPool,
    QTimer,
    Signal,
)

from app.hardware.usb import UsbDeviceMonitor


logger = logging.getLogger(__name__)


class _UsbPollSignals(QObject):
    completed = Signal(int, object)
    failed = Signal(int, object)


class _UsbPollTask(QRunnable):

    def __init__(
        self,
        device_monitor: UsbDeviceMonitor,
        device_id: str | None,
        generation: int,
        signals: _UsbPollSignals,
    ):
        super().__init__()
        self.device_monitor = device_monitor
        self.device_id = device_id
        self.generation = generation
        self.signals = signals

    def run(self) -> None:
        try:
            devices = self.device_monitor.get_devices()

            if self.device_id is None:
                current_state: bool | set[str] = {
                    device.windows_device_id
                    for device in devices
                }
            else:
                current_state = any(
                    device.windows_device_id == self.device_id
                    for device in devices
                )
        except Exception as error:
            self.signals.failed.emit(self.generation, error)
            return

        self.signals.completed.emit(self.generation, current_state)


def _wait_for_usb_polls() -> None:
    if not QThreadPool.globalInstance().waitForDone(2_000):
        logger.error("USB device polling did not finish before shutdown")


class UsbDevicePoller(QObject):

    state_ready = Signal(object)
    poll_failed = Signal(object)

    def __init__(
        self,
        device_monitor: UsbDeviceMonitor,
        device_id: str | None = None,
        parent: QObject | None = None,
    ):
        super().__init__(parent)

        self.device_monitor = device_monitor
        self.device_id = device_id
        self._generation = 0
        self._monitoring = False
        self._poll_in_flight = False

        application = QCoreApplication.instance()
        self._poll_signals = _UsbPollSignals(application)
        self._poll_signals.completed.connect(self._on_poll_completed)
        self._poll_signals.failed.connect(self._on_poll_failed)
        if application is not None:
            application.aboutToQuit.connect(_wait_for_usb_polls)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_device)

    def start(self, interval_ms: int = 500) -> None:
        self.validate_interval(interval_ms)
        self._generation += 1
        self._monitoring = True
        self.timer.start(interval_ms)
        self._check_device()

    def set_interval(self, interval_ms: int) -> None:
        self.validate_interval(interval_ms)
        self.timer.setInterval(interval_ms)

    def stop(self) -> None:
        self._monitoring = False
        self._generation += 1
        self.timer.stop()

    @staticmethod
    def validate_interval(interval_ms: int) -> None:
        if (
            not isinstance(interval_ms, int)
            or isinstance(interval_ms, bool)
            or not 1 <= interval_ms <= 2_147_483_647
        ):
            raise ValueError(
                "USB monitor polling interval must be between 1 and "
                "2147483647 milliseconds."
            )

    def _check_device(self) -> None:
        if not self._monitoring or self._poll_in_flight:
            return

        self._poll_in_flight = True
        QThreadPool.globalInstance().start(
            _UsbPollTask(
                device_monitor=self.device_monitor,
                device_id=self.device_id,
                generation=self._generation,
                signals=self._poll_signals,
            )
        )

    def _on_poll_completed(
        self,
        generation: int,
        current_state: bool | set[str],
    ) -> None:
        self._poll_in_flight = False

        if not self._monitoring or generation != self._generation:
            if self._monitoring:
                self._check_device()
            return

        self.state_ready.emit(current_state)

    def _on_poll_failed(self, generation: int, error: Exception) -> None:
        self._poll_in_flight = False

        if not self._monitoring or generation != self._generation:
            if self._monitoring:
                self._check_device()
            return

        self.poll_failed.emit(error)

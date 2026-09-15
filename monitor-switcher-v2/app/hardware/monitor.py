from abc import ABC, abstractmethod

from app.models.display import Display


class MonitorController(ABC):

    @abstractmethod
    def switch_input(self, display_id: str, input_id: str) -> None:
        pass


class DisplayDiscovery(ABC):

    @abstractmethod
    def get_displays(self) -> list[Display]:
        pass
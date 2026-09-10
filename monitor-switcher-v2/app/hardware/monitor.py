from abc import ABC, abstractmethod


class MonitorController(ABC):

    @abstractmethod
    def switch_input(self, input_id: str) -> None:
        pass
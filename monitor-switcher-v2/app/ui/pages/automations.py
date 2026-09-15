from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.models.automation import TriggerType, ActionType


class AutomationCard(QFrame):

    def __init__(self, automation):
        super().__init__()

        self.automation = automation

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Name
        name = QLabel(self.automation.name)
        name.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        # Status
        status = QLabel(
            "Enabled" if self.automation.enabled else "Disabled"
        )

        # Trigger
        trigger = self.automation.trigger

        if trigger.type == TriggerType.DEVICE_CONNECTED:
            trigger_text = "Device connects"
        elif trigger.type == TriggerType.DEVICE_DISCONNECTED:
            trigger_text = "Device disconnects"
        else:
            trigger_text = trigger.type.value

        trigger_label = QLabel(
            f"WHEN  {trigger_text}"
        )

        # Actions
        actions_label = QLabel("DO")

        layout.addWidget(name)
        layout.addWidget(status)
        layout.addWidget(trigger_label)
        layout.addWidget(actions_label)

        for action in self.automation.actions:
            if action.type == ActionType.SWITCH_INPUT:
                action_text = (
                    f"{action.display_id} → {action.input_id}"
                )

            elif action.type == ActionType.DO_NOTHING:
                action_text = "Do nothing"

            else:
                action_text = action.type.value

            layout.addWidget(
                QLabel(f"      {action_text}")
            )


class AutomationsPage(QWidget):

    def __init__(self, repository):
        super().__init__()

        self.repository = repository

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Automations")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(title)

        automations = self.repository.load_automations()

        if not automations:
            layout.addWidget(
                QLabel("No automations configured.")
            )
            return

        for automation in automations:
            layout.addWidget(
                AutomationCard(automation)
            )

        layout.addStretch()
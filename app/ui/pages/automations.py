from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.automations_card import AutomationCard
from app.ui.widgets.automation_editor import AutomationEditor


class AutomationsPage(QWidget):

    def __init__(
        self,
        repository,
        display_service,
        usb_service,
    ):
        super().__init__()

        self.repository = repository
        self.display_service = display_service
        self.usb_service = usb_service

        self._setup_ui()

    def _setup_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)

        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(28, 24, 28, 24)
        content_layout.setSpacing(14)

        header = QHBoxLayout()
        title_group = QVBoxLayout()
        title_group.setSpacing(4)

        title = QLabel("Automations")
        title.setObjectName("pageTitle")
        description = QLabel(
            "Choose what your displays do when a USB device connects or disconnects."
        )
        description.setObjectName("mutedText")
        description.setWordWrap(True)
        title_group.addWidget(title)
        title_group.addWidget(description)

        self.add_button = QPushButton("＋  Add automation")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self._add_automation)

        header.addLayout(title_group, 1)
        header.addWidget(self.add_button, 0, Qt.AlignmentFlag.AlignTop)
        content_layout.addLayout(header)

        self.summary = QLabel()
        self.summary.setObjectName("automationSummary")
        content_layout.addWidget(self.summary)

        self.automations_container = QWidget()
        self.automations_layout = QVBoxLayout(self.automations_container)
        self.automations_layout.setContentsMargins(0, 0, 0, 0)
        self.automations_layout.setSpacing(12)
        content_layout.addWidget(self.automations_container)
        content_layout.addStretch()

        scroll_area = QScrollArea()
        scroll_area.setObjectName("automationsScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(self.content)
        page_layout.addWidget(scroll_area)

        self.empty_state = QLabel(
            "No automations yet\n"
            "Add an automation to switch a display automatically when a device changes state."
        )
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setWordWrap(True)

        self._refresh_automations()

    def _refresh_automations(self):
        while self.automations_layout.count():
            item = self.automations_layout.takeAt(0)
            widget = item.widget()
            if widget is not None and widget is not self.empty_state:
                widget.deleteLater()

        automations = self.repository.load_automations()
        enabled_count = sum(automation.enabled for automation in automations)
        count = len(automations)
        if count == 0:
            self.summary.setText("Nothing is running yet")
            self.automations_layout.addWidget(self.empty_state)
            return

        automation_word = "automation" if count == 1 else "automations"
        self.summary.setText(
            f"{count} {automation_word}  ·  {enabled_count} enabled"
        )
        self.empty_state.setParent(None)

        for automation in automations:
            card = AutomationCard(
                automation,
                self.display_service,
                self.usb_service,
            )
            card.edit_requested.connect(self._edit_automation)
            card.delete_requested.connect(self._delete_automation)
            self.automations_layout.addWidget(card)

    def _edit_automation(self, automation):
        editor = AutomationEditor(
            self.display_service,
            self.usb_service,
            automation,
            self,
        )

        if editor.exec() != QDialog.DialogCode.Accepted:
            return

        updated_automation = editor.get_automation()
        automations = self.repository.load_automations()

        for index, existing_automation in enumerate(automations):
            if existing_automation.id == updated_automation.id:
                automations[index] = updated_automation
                break

        self.repository.save_automations(automations)
        self._refresh_automations()

    def _delete_automation(self, automation):
        result = QMessageBox.question(
            self,
            "Delete Automation",
            f"Are you sure you want to delete '{automation.name}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        automations = self.repository.load_automations()
        automations = [
            existing_automation
            for existing_automation in automations
            if existing_automation.id != automation.id
        ]

        self.repository.save_automations(automations)
        self._refresh_automations()

    def _add_automation(self):
        editor = AutomationEditor(
            self.display_service,
            self.usb_service,
            parent=self,
        )

        if editor.exec() != QDialog.DialogCode.Accepted:
            return

        automation = editor.get_automation()
        automations = self.repository.load_automations()
        automation.id = self._get_next_automation_id(automations)
        automations.append(automation)

        self.repository.save_automations(automations)
        self._refresh_automations()

    def _get_next_automation_id(self, automations):
        existing_ids = {
            automation.id
            for automation in automations
        }

        index = 1

        while f"automation-{index:03d}" in existing_ids:
            index += 1

        return f"automation-{index:03d}"

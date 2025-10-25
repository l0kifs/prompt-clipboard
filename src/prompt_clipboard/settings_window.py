from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QKeySequenceEdit,
    QPushButton,
    QVBoxLayout,
)

from prompt_clipboard.database import DatabaseManager


class SettingsWindow(QDialog):
    """Settings window for configuring application preferences."""

    hotkey_changed = Signal(str)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.hotkey_edit = QKeySequenceEdit(self)
        form_layout.addRow("Hotkey:", self.hotkey_edit)
        layout.addLayout(form_layout)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self._save_settings)
        layout.addWidget(self.save_button)

    def _load_settings(self):
        hotkey = self.db_manager.get_setting("hotkey", "Ctrl+Alt+I")
        self.hotkey_edit.setKeySequence(hotkey)

    def _save_settings(self):
        hotkey = self.hotkey_edit.keySequence().toString()
        self.db_manager.set_setting("hotkey", hotkey)
        self.hotkey_changed.emit(hotkey)
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        super().keyPressEvent(event)

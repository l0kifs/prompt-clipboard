from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QTextEdit,
)

from prompt_clipboard.config.logging import logger
from prompt_clipboard.database import DatabaseManager


class AddPromptDialog(QDialog):
    """Dialog for adding a new prompt."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Add New Prompt")
        self.setModal(True)

        layout = QFormLayout(self)
        self.body_edit = QTextEdit(self)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout.addRow("Prompt:", self.body_edit)
        layout.addRow(buttons)

    def _on_accept(self):
        body = self.body_edit.toPlainText().strip()
        if body:
            try:
                self.db_manager.add_prompt(body)
                logger.debug("Prompt added via dialog", body_length=len(body))
                self.accept()
            except Exception as e:
                logger.error("Failed to add prompt via dialog", error=str(e))
                self.reject()
        else:
            logger.debug("Empty prompt rejected in dialog")
            self.reject()

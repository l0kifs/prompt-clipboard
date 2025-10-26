from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QTextEdit,
)

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
            self.db_manager.add_prompt(body)
            self.accept()
        else:
            self.reject()

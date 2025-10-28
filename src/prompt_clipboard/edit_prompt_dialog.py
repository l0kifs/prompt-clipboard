from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QTextEdit,
)

from prompt_clipboard.database import DatabaseManager


class EditPromptDialog(QDialog):
    """Dialog for editing an existing prompt."""

    def __init__(
        self, db_manager: DatabaseManager, prompt_id: int, body: str, parent=None
    ):
        super().__init__(parent)
        self.db_manager = db_manager
        self.prompt_id = prompt_id
        self._setup_ui(body)

    def _setup_ui(self, body: str):
        self.setWindowTitle("Edit Prompt")
        self.setModal(True)

        layout = QFormLayout(self)
        self.body_edit = QTextEdit(self)
        self.body_edit.setPlainText(body)

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
            self.db_manager.update_prompt(self.prompt_id, body)
            self.accept()
        else:
            self.reject()

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from prompt_clipboard.add_prompt_dialog import AddPromptDialog
from prompt_clipboard.config.logging import logger
from prompt_clipboard.database import DatabaseManager
from prompt_clipboard.edit_prompt_dialog import EditPromptDialog


class PromptManagerWindow(QDialog):
    """Window for managing prompts (add, edit, delete)."""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._setup_ui()
        self._load_prompts()

    def _setup_ui(self):
        self.setWindowTitle("Manage Prompts")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        self.list = QListWidget(self)
        layout.addWidget(self.list)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add", self)
        self.edit_btn = QPushButton("Edit", self)
        self.delete_btn = QPushButton("Delete", self)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self._on_add)
        self.edit_btn.clicked.connect(self._on_edit)
        self.delete_btn.clicked.connect(self._on_delete)

    def _load_prompts(self):
        self.list.clear()
        rows = self.db_manager.get_all_prompts()

        for i, prompt in enumerate(rows):
            # Add visual separator between prompts (except before first)
            if i > 0:
                separator = QListWidgetItem("  ")
                separator.setFlags(Qt.ItemFlag.NoItemFlags)
                separator.setData(Qt.ItemDataRole.UserRole, None)
                self.list.addItem(separator)

            # Display prompt - replace newlines with space
            body_display = prompt.body.replace("\n", " ")[:200]
            item = QListWidgetItem(f"{body_display} [{prompt.usage_count}]")
            item.setData(Qt.ItemDataRole.UserRole, (prompt.id, prompt.body))
            self.list.addItem(item)

    def _on_add(self):
        dialog = AddPromptDialog(self.db_manager, self)
        if dialog.exec():
            self._load_prompts()

    def _on_edit(self):
        current = self.list.currentItem()
        if not current:
            QMessageBox.warning(self, "Warning", "Select a prompt to edit.")
            return

        data = current.data(Qt.ItemDataRole.UserRole)
        if data is None:  # Skip separator
            QMessageBox.warning(self, "Warning", "Select a prompt to edit.")
            return

        prompt_id, body = data
        dialog = EditPromptDialog(self.db_manager, prompt_id, body, self)
        if dialog.exec():
            self._load_prompts()

    def _on_delete(self):
        current = self.list.currentItem()
        if not current:
            QMessageBox.warning(self, "Warning", "Select a prompt to delete.")
            return

        data = current.data(Qt.ItemDataRole.UserRole)
        if data is None:  # Skip separator
            QMessageBox.warning(self, "Warning", "Select a prompt to delete.")
            return

        prompt_id, _ = data
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this prompt?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_prompt(prompt_id)
                logger.info("Prompt deleted via manager", prompt_id=prompt_id)
                self._load_prompts()
            except Exception as e:
                logger.error(
                    "Failed to delete prompt via manager",
                    prompt_id=prompt_id,
                    error=str(e),
                )
                QMessageBox.critical(self, "Error", f"Failed to delete prompt: {e}")

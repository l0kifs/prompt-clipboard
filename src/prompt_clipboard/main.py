import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from prompt_clipboard.config import settings
from prompt_clipboard.config.logging import logger
from prompt_clipboard.database import DatabaseManager
from prompt_clipboard.hotkey import HotkeyManager
from prompt_clipboard.settings_window import SettingsWindow


# Clipboard helper
def copy_to_clipboard(text):
    app = QApplication.instance() or QApplication([])
    cb = app.clipboard()
    cb.setText(text, QClipboard.Mode.Clipboard)


# Overlay UI
class Overlay(QWidget):
    def __init__(self, db_manager, hotkey_manager):
        super().__init__()
        self.db_manager = db_manager
        self.hotkey_manager = hotkey_manager
        # frameless, always-on-top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle(settings.app.name)
        self.setMinimumSize(400, 300)  # Set minimum size instead of fixed
        self.resize(600, 350)  # Set initial size
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Search prompts...")
        self.list = QListWidget(self)
        self.list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.add_btn = QPushButton("Add New Prompt", self)
        self.manage_btn = QPushButton("Manage Prompts", self)
        self.settings_btn = QPushButton("Settings", self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.search)
        layout.addWidget(self.list)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.manage_btn)
        btn_layout.addWidget(self.settings_btn)
        layout.addLayout(btn_layout)
        self.search.textChanged.connect(self.on_search)
        self.list.itemActivated.connect(self.on_activate)
        self.add_btn.clicked.connect(self.on_add)
        self.manage_btn.clicked.connect(self.on_manage)
        self.settings_btn.clicked.connect(self.on_settings)
        self.search.returnPressed.connect(self.on_search_enter)
        self.search.keyPressEvent = self.search_key_press
        self.list.keyPressEvent = self.list_key_press

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        super().keyPressEvent(event)

    def on_search(self, text):
        self.list.clear()
        if not text.strip():
            # Show all prompts when search is empty
            rows = self.db_manager.get_all_prompts()
            self.has_results = bool(rows)
            for prompt in rows:
                item = QListWidgetItem(f"{prompt.body[:120]} [{prompt.usage_count}]")
                item.setData(Qt.ItemDataRole.UserRole, (prompt.id, prompt.body))
                self.list.addItem(item)
            self.list.clearSelection()
            self.list.setCurrentRow(-1)
            return
        rows = self.db_manager.search_prompts(text)
        self.has_results = bool(rows)
        for prompt in rows:
            item = QListWidgetItem(f"{prompt.body[:120]} [{prompt.usage_count}]")
            item.setData(Qt.ItemDataRole.UserRole, (prompt.id, prompt.body))
            self.list.addItem(item)
        self.list.clearSelection()
        self.list.setCurrentRow(-1)

    def on_search_enter(self):
        text = self.search.text().strip()
        if text and not self.has_results:
            self.db_manager.add_prompt(text)
            self.on_search(text)

    def on_activate(self, item: QListWidgetItem):
        pid, body = item.data(Qt.ItemDataRole.UserRole)
        copy_to_clipboard(body)
        self.db_manager.increment_usage(pid)
        self.hide()

    def on_list_enter(self):
        selected = self.list.selectedItems()
        if not selected:
            current = self.list.currentItem()
            if current:
                selected = [current]
        if selected:
            bodies = []
            for item in selected:
                pid, body = item.data(Qt.ItemDataRole.UserRole)
                bodies.append(body)
                self.db_manager.increment_usage(pid)
            copy_to_clipboard("\n".join(bodies))
            self.hide()

    def on_add(self):
        dialog = AddPromptDialog(self.db_manager, self)
        dialog.exec()
        # Refresh search if needed
        self.on_search(self.search.text())

    def on_manage(self):
        manager = PromptManager(self.db_manager, self)
        manager.exec()
        self.on_search(self.search.text())

    def on_settings(self):
        settings_window = SettingsWindow(self.db_manager, self)
        settings_window.hotkey_changed.connect(self.hotkey_manager.update_hotkey)
        settings_window.exec()

    def search_key_press(self, event):
        if event.key() == Qt.Key.Key_Down:
            if self.list.count() > 0:
                self.list.setFocus()
            else:
                QLineEdit.keyPressEvent(self.search, event)
        else:
            QLineEdit.keyPressEvent(self.search, event)

    def list_key_press(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.on_list_enter()
        elif event.key() == Qt.Key.Key_Up:
            if self.list.currentRow() <= 0:
                self.search.setFocus()
            else:
                QListWidget.keyPressEvent(self.list, event)
        else:
            QListWidget.keyPressEvent(self.list, event)


class AddPromptDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add New Prompt")
        self.setModal(True)
        layout = QFormLayout(self)
        self.body_edit = QTextEdit(self)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow("Prompt:", self.body_edit)
        layout.addRow(buttons)

    def on_accept(self):
        body = self.body_edit.toPlainText().strip()
        if body:
            self.db_manager.add_prompt(body)
            self.accept()
        else:
            self.reject()


class EditPromptDialog(QDialog):
    def __init__(self, db_manager, pid, body, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.pid = pid
        self.setWindowTitle("Edit Prompt")
        self.setModal(True)
        layout = QFormLayout(self)
        self.body_edit = QTextEdit(self)
        self.body_edit.setPlainText(body)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow("Prompt:", self.body_edit)
        layout.addRow(buttons)

    def on_accept(self):
        body = self.body_edit.toPlainText().strip()
        if body:
            self.db_manager.update_prompt(self.pid, body)
            self.accept()
        else:
            self.reject()


class PromptManager(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
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
        self.load_prompts()
        self.add_btn.clicked.connect(self.on_add)
        self.edit_btn.clicked.connect(self.on_edit)
        self.delete_btn.clicked.connect(self.on_delete)

    def load_prompts(self):
        self.list.clear()
        rows = self.db_manager.get_all_prompts()
        for prompt in rows:
            item = QListWidgetItem(f"{prompt.body[:200]} [{prompt.usage_count}]")
            item.setData(Qt.ItemDataRole.UserRole, (prompt.id, prompt.body))
            self.list.addItem(item)

    def on_add(self):
        dialog = AddPromptDialog(self.db_manager, self)
        if dialog.exec():
            self.load_prompts()

    def on_edit(self):
        current = self.list.currentItem()
        if not current:
            QMessageBox.warning(self, "Warning", "Select a prompt to edit.")
            return
        pid, body = current.data(Qt.ItemDataRole.UserRole)
        dialog = EditPromptDialog(self.db_manager, pid, body, self)
        if dialog.exec():
            self.load_prompts()

    def on_delete(self):
        current = self.list.currentItem()
        if not current:
            QMessageBox.warning(self, "Warning", "Select a prompt to delete.")
            return
        pid, _ = current.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this prompt?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_prompt(pid)
            self.load_prompts()


def main():
    logger.info("Application starting")
    db_manager = DatabaseManager(settings.database.path)
    app = QApplication(sys.argv)

    # Get hotkey from settings or use default
    hotkey_sequence = db_manager.get_setting("hotkey") or "Ctrl+Alt+I"
    hk = HotkeyManager(hotkey_sequence)

    overlay = Overlay(db_manager, hk)

    def show_overlay():
        overlay.show()
        overlay.activateWindow()
        overlay.raise_()
        overlay.search.clear()
        overlay.on_search(overlay.search.text())
        overlay.search.setFocus()

    hk.hotkey_pressed.connect(show_overlay)
    hk.start()

    # Seed example prompt if DB empty
    if db_manager.is_empty():
        db_manager.add_prompt(settings.app.seed_prompt)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from prompt_clipboard.add_prompt_dialog import AddPromptDialog
from prompt_clipboard.config import settings
from prompt_clipboard.config.logging import logger
from prompt_clipboard.database import DatabaseManager
from prompt_clipboard.hotkey import HotkeyManager
from prompt_clipboard.prompt_manager_window import PromptManagerWindow
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
        # Track selection order
        self.selection_order = []  # List of item widgets in order of selection
        # frameless, always-on-top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle(settings.app.name)
        self.setMinimumSize(400, 300)  # Set minimum size instead of fixed
        self.resize(900, 525)  # Set initial size
        self.search = QLineEdit(self)
        self.search.setPlaceholderText("Search prompts...")
        self.list = QListWidget(self)
        self.list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.list.setToolTip(
            "Используйте Space для выбора/отмены, Ctrl+Click для множественного выбора"
        )
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
        self.list.itemSelectionChanged.connect(self.on_selection_changed)
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

    def on_selection_changed(self):
        """Track the order of selection."""
        current_selected = self.list.selectedItems()

        # Find newly selected items (not in selection_order yet)
        for item in current_selected:
            if item not in self.selection_order:
                self.selection_order.append(item)

        # Remove deselected items (in selection_order but not in current_selected)
        items_to_remove = []
        for item in self.selection_order:
            if item not in current_selected:
                items_to_remove.append(item)

        for item in items_to_remove:
            self.selection_order.remove(item)

    def on_search(self, text):
        self.list.clear()
        self.selection_order = []  # Reset selection order on new search
        text = text.strip()

        if not text:
            # Show all prompts when search is empty
            rows = self.db_manager.get_all_prompts()
            self.has_results = bool(rows)
            self._display_prompts(rows)
            return

        # Search by phrase
        result = self.db_manager.search_prompts(text)

        if not result:
            # No matches - show all prompts
            rows = self.db_manager.get_all_prompts()
            self.has_results = False
            self._display_prompts(rows)
        else:
            # Show matched prompts with related ones grouped together
            matched, related_map, cross_refs = result
            self.has_results = True
            self._display_search_results(matched, related_map, cross_refs)

        self.list.clearSelection()
        self.list.setCurrentRow(-1)

    def _display_prompts(self, prompts):
        """Display a simple list of prompts."""
        for i, prompt in enumerate(prompts):
            # Add visual separator between prompts (except before first)
            if i > 0:
                separator = QListWidgetItem("  ")  # Small visual gap
                separator.setFlags(Qt.ItemFlag.NoItemFlags)
                separator.setData(Qt.ItemDataRole.UserRole, None)
                self.list.addItem(separator)

            # Display prompt - replace newlines with space for single-line display
            body_display = prompt.body.replace("\n", " ")[:120]
            item = QListWidgetItem(f"{body_display} [{prompt.usage_count}]")
            item.setData(Qt.ItemDataRole.UserRole, (prompt.id, prompt.body))
            self.list.addItem(item)

    def _display_search_results(self, matched, related_map, cross_refs):
        """Display matched prompts with their related prompts grouped."""
        displayed_ids = set()
        all_prompts = self.db_manager.get_all_prompts()
        matched_ids = {p.id for p in matched}

        # Create a map for quick access to prompts by id
        prompt_map = {p.id: p for p in matched}

        # Group matched prompts that are connected to each other
        groups = []
        ungrouped = set(p.id for p in matched)

        while ungrouped:
            # Start a new group with first ungrouped prompt
            start_id = next(iter(ungrouped))
            group = {start_id}
            ungrouped.remove(start_id)

            # Expand group to include all connected prompts
            changed = True
            while changed:
                changed = False
                to_add = set()
                for pid in group:
                    if pid in cross_refs:
                        for connected_prompt, _ in cross_refs[pid]:
                            if connected_prompt.id in ungrouped:
                                to_add.add(connected_prompt.id)
                                changed = True
                for pid in to_add:
                    group.add(pid)
                    ungrouped.remove(pid)

            groups.append(group)

        # Sort groups by maximum usage_count within each group (descending)
        def get_group_max_usage(group):
            return max(prompt_map[pid].usage_count for pid in group)

        groups.sort(key=get_group_max_usage, reverse=True)

        # Display each group
        first_group = True
        for group in groups:
            if not first_group:
                separator = QListWidgetItem("─" * 60)
                separator.setFlags(Qt.ItemFlag.NoItemFlags)
                separator.setData(Qt.ItemDataRole.UserRole, None)
                self.list.addItem(separator)
            first_group = False

            # Sort prompts within group by usage_count (descending)
            group_prompts = [p for p in matched if p.id in group]
            group_prompts.sort(key=lambda p: p.usage_count, reverse=True)

            # Display all prompts in this group
            first_in_group = True
            for prompt in group_prompts:
                if prompt.id in displayed_ids:
                    continue

                # Add small separator between prompts in group (but not before first)
                if not first_in_group:
                    separator = QListWidgetItem("  ")
                    separator.setFlags(Qt.ItemFlag.NoItemFlags)
                    separator.setData(Qt.ItemDataRole.UserRole, None)
                    self.list.addItem(separator)
                first_in_group = False

                # Add matched prompt with marker - replace newlines
                body_display = prompt.body.replace("\n", " ")[:120]
                item = QListWidgetItem(f"✓ {body_display} [{prompt.usage_count}]")
                item.setData(Qt.ItemDataRole.UserRole, (prompt.id, prompt.body))
                self.list.addItem(item)
                displayed_ids.add(prompt.id)

                # Add related prompts (non-matched only)
                if prompt.id in related_map:
                    for related_prompt, strength in related_map[prompt.id]:
                        if (
                            related_prompt.id not in displayed_ids
                            and related_prompt.id not in matched_ids
                        ):
                            body_display = related_prompt.body.replace("\n", " ")[:120]
                            item = QListWidgetItem(
                                f"  ↳ {body_display} [{related_prompt.usage_count}] (связь: {strength})"
                            )
                            item.setData(
                                Qt.ItemDataRole.UserRole,
                                (related_prompt.id, related_prompt.body),
                            )
                            self.list.addItem(item)
                            displayed_ids.add(related_prompt.id)

        # Add remaining prompts with separator if there were any groups
        remaining = [p for p in all_prompts if p.id not in displayed_ids]
        if remaining:
            if not first_group:
                separator = QListWidgetItem("─" * 60)
                separator.setFlags(Qt.ItemFlag.NoItemFlags)
                separator.setData(Qt.ItemDataRole.UserRole, None)
                self.list.addItem(separator)

            for i, prompt in enumerate(remaining):
                # Add small separator between remaining prompts
                if i > 0:
                    separator = QListWidgetItem("  ")
                    separator.setFlags(Qt.ItemFlag.NoItemFlags)
                    separator.setData(Qt.ItemDataRole.UserRole, None)
                    self.list.addItem(separator)

                body_display = prompt.body.replace("\n", " ")[:120]
                item = QListWidgetItem(f"{body_display} [{prompt.usage_count}]")
                item.setData(Qt.ItemDataRole.UserRole, (prompt.id, prompt.body))
                self.list.addItem(item)

    def on_search_enter(self):
        text = self.search.text().strip()
        if text and not self.has_results:
            self.db_manager.add_prompt(text)
            self.on_search(text)

    def on_activate(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data is None:  # Skip separator items
            return
        pid, body = data
        try:
            copy_to_clipboard(body)
            self.db_manager.increment_usage(pid)
            logger.debug(
                "Prompt activated and copied to clipboard",
                prompt_id=pid,
                body_length=len(body),
            )
            self.hide()
        except Exception as e:
            logger.error("Failed to activate prompt", prompt_id=pid, error=str(e))

    def on_list_enter(self):
        # Use selection_order for the order of copying
        selected = (
            self.selection_order if self.selection_order else self.list.selectedItems()
        )

        if not selected:
            current = self.list.currentItem()
            if current:
                selected = [current]

        if selected:
            bodies = []
            prompt_ids = []
            for item in selected:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data is None:  # Skip separator items
                    continue
                pid, body = data
                bodies.append(body)
                prompt_ids.append(pid)
                self.db_manager.increment_usage(pid)

            # Create relations if multiple prompts selected
            if len(prompt_ids) > 1:
                self.db_manager.add_prompt_relations(prompt_ids)

            if bodies:  # Only copy if there are actual prompts
                try:
                    copy_to_clipboard("\n".join(bodies))
                    logger.info(
                        "Multiple prompts copied to clipboard",
                        prompts_count=len(bodies),
                        total_length=sum(len(b) for b in bodies),
                    )
                    self.hide()
                except Exception as e:
                    logger.error(
                        "Failed to copy multiple prompts",
                        prompts_count=len(bodies),
                        error=str(e),
                    )

    def on_add(self):
        dialog = AddPromptDialog(self.db_manager, self)
        dialog.exec()
        # Refresh search if needed
        self.on_search(self.search.text())

    def on_manage(self):
        manager = PromptManagerWindow(self.db_manager, self)
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
        elif event.key() == Qt.Key.Key_Space:
            # Toggle selection of current item with Space key
            current = self.list.currentItem()
            if current and current.data(Qt.ItemDataRole.UserRole) is not None:
                current.setSelected(not current.isSelected())
        elif event.key() == Qt.Key.Key_Up:
            if self.list.currentRow() <= 0:
                self.search.setFocus()
            else:
                QListWidget.keyPressEvent(self.list, event)
        else:
            QListWidget.keyPressEvent(self.list, event)


def main():
    logger.info("Application starting")

    try:
        db_manager = DatabaseManager(settings.database.path)
    except Exception as e:
        logger.critical("Failed to initialize database manager", error=str(e))
        sys.exit(1)

    app = QApplication(sys.argv)

    # Get hotkey from settings or use default
    hotkey_sequence = db_manager.get_setting("hotkey") or "Ctrl+Alt+I"
    logger.info("Hotkey configured", hotkey=hotkey_sequence)

    try:
        hk = HotkeyManager(hotkey_sequence)
    except Exception as e:
        logger.error(
            "Failed to initialize hotkey manager", hotkey=hotkey_sequence, error=str(e)
        )
        sys.exit(1)

    overlay = Overlay(db_manager, hk)

    def show_overlay():
        try:
            overlay.show()
            overlay.activateWindow()
            overlay.raise_()
            overlay.search.clear()
            overlay.on_search(overlay.search.text())
            overlay.search.setFocus()
            logger.debug("Overlay displayed")
        except Exception as e:
            logger.error("Failed to show overlay", error=str(e))

    hk.hotkey_pressed.connect(show_overlay)
    hk.start()

    # Seed example prompt if DB empty
    if db_manager.is_empty():
        db_manager.add_prompt(settings.app.seed_prompt)
        logger.info("Database seeded with default prompt")

    logger.info("Application started successfully")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

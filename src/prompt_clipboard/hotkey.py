from pynput import keyboard
from PySide6.QtCore import QObject, Signal

from prompt_clipboard.config.logging import logger


class HotkeyManager(QObject):
    """Manages global hotkey detection and emits signal when triggered."""

    hotkey_pressed = Signal()

    def __init__(self, hotkey_sequence: str = "Ctrl+Alt+I"):
        super().__init__()
        self.listener = None
        self.hotkey_sequence = hotkey_sequence
        self._parse_hotkey(hotkey_sequence)

    def _parse_hotkey(self, sequence: str):
        """Parse hotkey sequence string into modifiers and key."""
        parts = sequence.split("+")
        self.modifiers = set()
        self.trigger_key = None

        modifier_map = {
            "ctrl": keyboard.Key.ctrl,
            "alt": keyboard.Key.alt,
            "shift": keyboard.Key.shift,
            "meta": keyboard.Key.cmd,
        }

        for part in parts:
            part_lower = part.strip().lower()
            if part_lower in modifier_map:
                self.modifiers.add(modifier_map[part_lower])
            else:
                self.trigger_key = part.strip().lower()

    def update_hotkey(self, hotkey_sequence: str):
        """Update hotkey sequence and restart listener."""
        self.stop()
        self.hotkey_sequence = hotkey_sequence
        self._parse_hotkey(hotkey_sequence)
        self.start()

    def start(self):
        pressed = set()

        def _on_press(k):
            pressed.add(k)
            logger.debug(f"Pressed: {k}, Modifiers: {pressed}")

            try:
                # Check if all required modifiers are pressed
                if not self.modifiers.issubset(pressed):
                    return

                # Check if trigger key matches
                key_char = None
                if hasattr(k, "char") and k.char:
                    key_char = k.char.lower()
                elif isinstance(k, keyboard.KeyCode):
                    key_char = getattr(k, "char", "").lower()

                if key_char == self.trigger_key:
                    logger.debug("Hotkey triggered!")
                    self.hotkey_pressed.emit()
            except Exception as e:
                logger.error(f"Error in hotkey check: {e}")

        def _on_release(k):
            logger.debug(f"Released: {k}")
            if k in pressed:
                pressed.remove(k)

        self.listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()

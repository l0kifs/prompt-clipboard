from PySide6.QtCore import QObject, Signal
from pynput import keyboard

from prompt_clipboard.config.logging import logger


# Global hotkey manager (Ctrl+Alt+I)
class HotkeyManager(QObject):
    hotkey_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.listener = None

    def start(self):
        pressed = set()

        def _on_press(k):
            pressed.add(k)
            logger.debug(f"Pressed: {k}, Modifiers: {pressed}")
            # check modifiers + 'i'
            try:
                if (
                    keyboard.Key.ctrl in pressed
                    and keyboard.Key.alt in pressed
                    and k == keyboard.KeyCode.from_char("i")
                ):
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

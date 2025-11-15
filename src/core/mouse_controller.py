"""MouseController - Maus-Steuerung mit pynput."""
from typing import Optional, Tuple
from pynput import mouse
from pynput.mouse import Button, Listener


class MouseController:
    """Wrapper um pynput.mouse für Maus-Steuerung."""

    def __init__(self):
        self._mouse = mouse.Controller()
        self._picked_position: Optional[Tuple[int, int]] = None
        self._listener: Optional[Listener] = None

    def get_current_position(self) -> Tuple[int, int]:
        """Gibt die aktuelle Mausposition zurück."""
        return self._mouse.position

    def click(self, button: str, click_type: str, position: Optional[Tuple[int, int]] = None) -> None:
        """
        Führt einen Click aus.

        Args:
            button: "left", "right" oder "middle"
            click_type: "single", "double" oder "triple"
            position: Optional tuple (x, y). Wenn None, wird an aktueller Position geklickt.
        """
        # Position setzen falls angegeben
        if position is not None:
            self._mouse.position = position

        # Button-Mapping
        button_map = {
            "left": Button.left,
            "right": Button.right,
            "middle": Button.middle
        }
        mouse_button = button_map.get(button.lower(), Button.left)

        # Click-Type ausführen
        if click_type.lower() == "single":
            self._mouse.click(mouse_button, 1)
        elif click_type.lower() == "double":
            self._mouse.click(mouse_button, 2)
        elif click_type.lower() == "triple":
            self._mouse.click(mouse_button, 3)
        else:
            # Default: single click
            self._mouse.click(mouse_button, 1)

    def pick_location(self) -> Optional[Tuple[int, int]]:
        """
        Blockiert bis der User klickt und gibt dann die Position zurück.
        Wird in einem separaten Thread aufgerufen.

        Returns:
            Tuple (x, y) der geklickten Position oder None wenn abgebrochen
        """
        self._picked_position = None
        self._listener = None

        def on_click(x, y, button, pressed):
            if pressed and button == Button.left:
                self._picked_position = (x, y)
                return False  # Listener stoppen

        # Listener starten
        self._listener = Listener(on_click=on_click)
        self._listener.start()
        self._listener.join()  # Warten bis Click erfolgt

        return self._picked_position

    def cancel_pick_location(self) -> None:
        """Bricht das Pick Location ab."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None


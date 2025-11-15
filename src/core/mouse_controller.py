"""MouseController - Maus-Steuerung mit pynput."""
import ctypes
from ctypes import wintypes
from typing import Optional, Tuple
from pynput import mouse
from pynput.mouse import Button


class MouseController:
    """Wrapper um pynput.mouse für Maus-Steuerung."""

    def __init__(self):
        self._mouse = mouse.Controller()
        self._picked_position: Optional[Tuple[int, int]] = None

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
        # Negative Koordinaten sind erlaubt (Multi-Monitor-Setups)
        if position is not None:
            try:
                self._mouse.position = position
            except Exception as e:
                # Falls pynput Probleme hat, Windows-API direkt verwenden
                try:
                    import ctypes
                    ctypes.windll.user32.SetCursorPos(int(position[0]), int(position[1]))
                except Exception:
                    raise ValueError(f"Konnte Mausposition nicht setzen: {position}") from e

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

    def pick_location(self, ignore_rects: Optional[list[Tuple[int, int, int, int]]] = None) -> Optional[Tuple[int, int]]:
        """
        Wartet auf einen Linksklick und gibt dann die Position zurück.
        Verwendet direkte Windows-API-Abfrage (GetAsyncKeyState) für Zuverlässigkeit.
        
        Args:
            ignore_rects: Optional Liste von (x, y, width, height) - Klicks in diesen Bereichen werden ignoriert
        
        Returns:
            Tuple (x, y) der geklickten Position oder None wenn abgebrochen
        """
        try:
            import ctypes
            import time
            
            user32 = ctypes.windll.user32
            VK_LBUTTON = 0x01  # Linke Maustaste
            
            # Warten bis Maustaste losgelassen (falls gerade gedrückt)
            while user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                time.sleep(0.01)
            
            # Warten auf Linksklick (Taste wird gedrückt)
            timeout = 60  # 60 Sekunden Timeout
            elapsed = 0
            
            while elapsed < timeout:
                # Prüfen ob linke Maustaste gedrückt wurde
                if user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                    # Maustaste ist gedrückt - Position holen
                    class POINT(ctypes.Structure):
                        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
                    
                    point = POINT()
                    user32.GetCursorPos(ctypes.byref(point))
                    x, y = point.x, point.y
                    
                    # Prüfen ob in Ignore-Bereich
                    if ignore_rects is not None:
                        in_ignore_area = False
                        for rect_x, rect_y, rect_w, rect_h in ignore_rects:
                            if rect_x <= x <= rect_x + rect_w and rect_y <= y <= rect_y + rect_h:
                                in_ignore_area = True
                                break
                        
                        if in_ignore_area:
                            # In Ignore-Bereich - warten bis Taste losgelassen
                            while user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                                time.sleep(0.01)
                            continue  # Weiter warten auf nächsten Klick
                    
                    # Gültiger Klick - warten bis Maustaste losgelassen
                    while user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000:
                        time.sleep(0.01)
                    
                    return (x, y)
                
                time.sleep(0.01)
                elapsed += 0.01
            
            # Timeout
            return None
            
        except Exception as e:
            print(f"Fehler bei pick_location: {e}")
            # Fallback: aktuelle Position
            try:
                return self.get_current_position()
            except Exception:
                return None


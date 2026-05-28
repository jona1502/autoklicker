"""HotkeyManager - Global Hotkey Registration mit keyboard Library."""
import keyboard
from typing import Optional, Callable, List


class HotkeyManager:
    """Verwaltet globale Hotkeys für die Anwendung."""

    def __init__(self):
        """Initialisiert den HotkeyManager."""
        self._registered_hotkeys: dict[str, Callable] = {}
        self._start_hotkey = "f6"
        self._stop_hotkey = "f7"
        self._modifiers: List[str] = []

    def register_hotkey(self, key: str, callback: Callable, modifiers: Optional[List[str]] = None):
        """
        Registriert einen globalen Hotkey.

        Args:
            key: Taste (z.B. "f6", "space")
            callback: Funktion die aufgerufen wird
            modifiers: Liste von Modifier-Keys (z.B. ["ctrl", "alt"])
        """
        # Alten Hotkey entfernen falls vorhanden
        hotkey_str = self._build_hotkey_string(key, modifiers)
        if hotkey_str in self._registered_hotkeys:
            self.unregister_hotkey(key, modifiers)

        # Neuen Hotkey registrieren
        try:
            # Wrapper um sicherzustellen dass der Callback im richtigen Thread läuft
            def safe_callback():
                try:
                    callback()
                except Exception as e:
                    print(f"Fehler im Hotkey-Callback: {e}")
            
            keyboard.add_hotkey(hotkey_str, safe_callback, suppress=False)
            self._registered_hotkeys[hotkey_str] = safe_callback
            print(f"OK: Hotkey registriert: {hotkey_str}")
        except Exception as e:
            print(f"FEHLER: Hotkey konnte nicht registriert werden {hotkey_str}: {e}")
            print(f"  Hinweis: App muss ggf. mit Admin-Rechten gestartet werden!")

    def unregister_hotkey(self, key: str, modifiers: Optional[List[str]] = None):
        """
        Entfernt einen registrierten Hotkey.

        Args:
            key: Taste
            modifiers: Liste von Modifier-Keys
        """
        hotkey_str = self._build_hotkey_string(key, modifiers)
        if hotkey_str in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey_str)
                del self._registered_hotkeys[hotkey_str]
            except Exception as e:
                print(f"Fehler beim Entfernen des Hotkeys {hotkey_str}: {e}")

    def set_start_hotkey(self, key: str, modifiers: Optional[List[str]] = None, callback: Optional[Callable] = None):
        """
        Setzt den Start-Hotkey.

        Args:
            key: Taste (z.B. "f6")
            modifiers: Liste von Modifier-Keys
            callback: Callback-Funktion
        """
        # Alten Hotkey entfernen
        if self._start_hotkey:
            old_modifiers = self._modifiers if self._start_hotkey == key else None
            self.unregister_hotkey(self._start_hotkey, old_modifiers)

        self._start_hotkey = key
        if modifiers:
            self._modifiers = modifiers
        else:
            self._modifiers = []

        if callback:
            self.register_hotkey(key, callback, modifiers)

    def set_stop_hotkey(self, key: str, modifiers: Optional[List[str]] = None, callback: Optional[Callable] = None):
        """
        Setzt den Stop-Hotkey.

        Args:
            key: Taste (z.B. "f6")
            modifiers: Liste von Modifier-Keys
            callback: Callback-Funktion
        """
        # Alten Hotkey entfernen
        if self._stop_hotkey:
            old_modifiers = self._modifiers if self._stop_hotkey == key else None
            self.unregister_hotkey(self._stop_hotkey, old_modifiers)

        self._stop_hotkey = key
        if modifiers:
            self._modifiers = modifiers
        else:
            self._modifiers = []

        if callback:
            self.register_hotkey(key, callback, modifiers)

    def unregister_all(self):
        """Entfernt alle registrierten Hotkeys."""
        for hotkey_str in list(self._registered_hotkeys.keys()):
            try:
                keyboard.remove_hotkey(hotkey_str)
            except Exception:
                pass
        self._registered_hotkeys.clear()

    @staticmethod
    def _build_hotkey_string(key: str, modifiers: Optional[List[str]] = None) -> str:
        """
        Baut einen Hotkey-String für die keyboard Library.

        Args:
            key: Taste
            modifiers: Liste von Modifier-Keys

        Returns:
            Hotkey-String (z.B. "ctrl+alt+f6")
        """
        if modifiers:
            return "+".join(modifiers + [key])
        return key

    def get_start_hotkey_string(self) -> str:
        """Gibt den Start-Hotkey als String zurück."""
        return self._build_hotkey_string(self._start_hotkey, self._modifiers if self._modifiers else None)

    def get_stop_hotkey_string(self) -> str:
        """Gibt den Stop-Hotkey als String zurück."""
        return self._build_hotkey_string(self._stop_hotkey, self._modifiers if self._modifiers else None)


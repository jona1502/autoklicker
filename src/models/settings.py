"""AppSettings Model für Einstellungen."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppSettings:
    """Speichert alle Anwendungseinstellungen."""
    # Click Interval Defaults
    default_hours: int = 0
    default_minutes: int = 0
    default_seconds: int = 0
    default_milliseconds: int = 0

    # Click Options Defaults
    default_mouse_button: str = "left"  # "left", "right", "middle"
    default_click_type: str = "single"  # "single", "double", "triple"

    # Click Repeat Defaults
    default_repeat_count: int = 1
    default_repeat_until_stopped: bool = True

    # Cursor Position Defaults
    default_use_current_location: bool = True
    default_pick_x: int = 0
    default_pick_y: int = 0

    # Hotkey Settings
    start_hotkey: str = "f6"
    stop_hotkey: str = "f7"
    hotkey_modifiers: list[str] = field(default_factory=list)  # ["ctrl", "alt", "shift"]

    # General Settings
    remember_last_settings: bool = True

    def to_dict(self) -> dict:
        """Konvertiert Settings zu Dictionary für JSON-Serialisierung."""
        return {
            "default_hours": self.default_hours,
            "default_minutes": self.default_minutes,
            "default_seconds": self.default_seconds,
            "default_milliseconds": self.default_milliseconds,
            "default_mouse_button": self.default_mouse_button,
            "default_click_type": self.default_click_type,
            "default_repeat_count": self.default_repeat_count,
            "default_repeat_until_stopped": self.default_repeat_until_stopped,
            "default_use_current_location": self.default_use_current_location,
            "default_pick_x": self.default_pick_x,
            "default_pick_y": self.default_pick_y,
            "start_hotkey": self.start_hotkey,
            "stop_hotkey": self.stop_hotkey,
            "hotkey_modifiers": self.hotkey_modifiers,
            "remember_last_settings": self.remember_last_settings
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        """Erstellt AppSettings aus Dictionary."""
        return cls(
            default_hours=data.get("default_hours", 0),
            default_minutes=data.get("default_minutes", 0),
            default_seconds=data.get("default_seconds", 0),
            default_milliseconds=data.get("default_milliseconds", 0),
            default_mouse_button=data.get("default_mouse_button", "left"),
            default_click_type=data.get("default_click_type", "single"),
            default_repeat_count=data.get("default_repeat_count", 1),
            default_repeat_until_stopped=data.get("default_repeat_until_stopped", True),
            default_use_current_location=data.get("default_use_current_location", True),
            default_pick_x=data.get("default_pick_x", 0),
            default_pick_y=data.get("default_pick_y", 0),
            start_hotkey=data.get("start_hotkey", "f6"),
            stop_hotkey=data.get("stop_hotkey", "f7"),
            hotkey_modifiers=data.get("hotkey_modifiers", []),
            remember_last_settings=data.get("remember_last_settings", True)
        )


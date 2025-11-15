"""ClickEvent Model für Record & Playback."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ClickEvent:
    """Repräsentiert ein einzelnes Click-Event für Recording."""
    position: tuple[int, int]  # (x, y)
    button: str  # "left", "right", "middle"
    click_type: str  # "single", "double", "triple"
    timestamp: datetime  # Zeitpunkt des Events
    delay_from_previous: float = 0.0  # Verzögerung vom vorherigen Event in Sekunden

    def to_dict(self) -> dict:
        """Konvertiert ClickEvent zu Dictionary für JSON-Serialisierung."""
        return {
            "position": self.position,
            "button": self.button,
            "click_type": self.click_type,
            "timestamp": self.timestamp.isoformat(),
            "delay_from_previous": self.delay_from_previous
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ClickEvent":
        """Erstellt ClickEvent aus Dictionary."""
        return cls(
            position=tuple(data["position"]),
            button=data["button"],
            click_type=data["click_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            delay_from_previous=data.get("delay_from_previous", 0.0)
        )


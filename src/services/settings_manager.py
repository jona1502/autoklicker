"""SettingsManager - JSON-basierte Persistierung der Einstellungen."""
import json
import os
from pathlib import Path
from typing import Optional

from src.models.settings import AppSettings


class SettingsManager:
    """Verwaltet das Speichern und Laden von Einstellungen."""

    def __init__(self, settings_file: Optional[str] = None):
        """
        Initialisiert den SettingsManager.

        Args:
            settings_file: Pfad zur Settings-Datei. Default: data/settings.json
        """
        if settings_file is None:
            # Default: data/settings.json relativ zum Projekt-Root
            project_root = Path(__file__).parent.parent.parent
            settings_file = project_root / "data" / "settings.json"
        
        self._settings_file = Path(settings_file)
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Stellt sicher, dass das data-Verzeichnis existiert."""
        self._settings_file.parent.mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> AppSettings:
        """
        Lädt die Einstellungen aus der JSON-Datei.

        Returns:
            AppSettings Objekt
        """
        if not self._settings_file.exists():
            return self.get_default_settings()

        try:
            with open(self._settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return AppSettings.from_dict(data)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            # Bei Fehler: Default-Settings zurückgeben
            print(f"Fehler beim Laden der Settings: {e}")
            return self.get_default_settings()

    def save_settings(self, settings: AppSettings) -> bool:
        """
        Speichert die Einstellungen in die JSON-Datei.

        Args:
            settings: AppSettings Objekt

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Fehler beim Speichern der Settings: {e}")
            return False

    @staticmethod
    def get_default_settings() -> AppSettings:
        """
        Gibt die Standard-Einstellungen zurück.

        Returns:
            AppSettings mit Default-Werten
        """
        return AppSettings()


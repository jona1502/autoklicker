"""ClickerEngine - Thread-basierte Click-Engine."""
import threading
import time
from datetime import timedelta
from typing import Optional, Callable, Tuple

from src.core.mouse_controller import MouseController


class ClickerEngine:
    """Thread-basierte Click-Engine für automatisches Klicken."""

    def __init__(self, mouse_controller: MouseController):
        """
        Initialisiert die Click-Engine.

        Args:
            mouse_controller: MouseController Instanz
        """
        self._mouse_controller = mouse_controller
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_running = False

        # Click-Parameter
        self._interval = timedelta(seconds=0.1)  # Default: 100ms
        self._mouse_button = "left"
        self._click_type = "single"
        self._repeat_count = -1  # -1 = unendlich
        self._target_position: Optional[Tuple[int, int]] = None
        self._current_position: Optional[Tuple[int, int]] = None

        # Callbacks
        self._on_click_callback: Optional[Callable] = None
        self._on_finished_callback: Optional[Callable] = None

    @property
    def is_running(self) -> bool:
        """Gibt zurück, ob die Engine läuft."""
        return self._is_running

    @property
    def interval(self) -> timedelta:
        """Gibt das aktuelle Intervall zurück."""
        return self._interval

    @interval.setter
    def interval(self, value: timedelta):
        """Setzt das Intervall."""
        if value.total_seconds() < 0.001:  # Minimum 1ms
            value = timedelta(seconds=0.001)
        self._interval = value

    @property
    def mouse_button(self) -> str:
        """Gibt den Maus-Button zurück."""
        return self._mouse_button

    @mouse_button.setter
    def mouse_button(self, value: str):
        """Setzt den Maus-Button."""
        self._mouse_button = value

    @property
    def click_type(self) -> str:
        """Gibt den Click-Typ zurück."""
        return self._click_type

    @click_type.setter
    def click_type(self, value: str):
        """Setzt den Click-Typ."""
        self._click_type = value

    @property
    def repeat_count(self) -> int:
        """Gibt die Wiederholungsanzahl zurück (-1 = unendlich)."""
        return self._repeat_count

    @repeat_count.setter
    def repeat_count(self, value: int):
        """Setzt die Wiederholungsanzahl (-1 für unendlich)."""
        self._repeat_count = value

    @property
    def target_position(self) -> Optional[Tuple[int, int]]:
        """Gibt die Ziel-Position zurück (None = aktuelle Position)."""
        return self._target_position

    @target_position.setter
    def target_position(self, value: Optional[Tuple[int, int]]):
        """Setzt die Ziel-Position (None = aktuelle Position)."""
        self._target_position = value

    def set_interval_from_components(self, hours: int, minutes: int, seconds: int, milliseconds: int):
        """
        Setzt das Intervall aus einzelnen Komponenten.

        Args:
            hours: Stunden
            minutes: Minuten
            seconds: Sekunden
            milliseconds: Millisekunden
        """
        total_seconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000.0)
        if total_seconds < 0.001:
            total_seconds = 0.001  # Minimum 1ms
        self._interval = timedelta(seconds=total_seconds)

    def set_on_click_callback(self, callback: Optional[Callable]):
        """Setzt einen Callback, der bei jedem Click aufgerufen wird."""
        self._on_click_callback = callback

    def set_on_finished_callback(self, callback: Optional[Callable]):
        """Setzt einen Callback, der aufgerufen wird, wenn das Klicken beendet ist."""
        self._on_finished_callback = callback

    def start(self):
        """Startet die Click-Engine in einem separaten Thread."""
        if self._is_running:
            return

        # Position speichern wenn "Current location" verwendet wird
        if self._target_position is None:
            self._current_position = self._mouse_controller.get_current_position()

        self._stop_event.clear()
        self._is_running = True
        self._thread = threading.Thread(target=self._click_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stoppt die Click-Engine - garantiert."""
        if not self._is_running:
            return

        # Stop-Event setzen (wichtig: ZUERST!)
        self._stop_event.set()
        
        # Flag setzen
        self._is_running = False

        # Thread sicher beenden
        if self._thread is not None and self._thread.is_alive():
            # Warten bis Thread beendet ist (max 2 Sekunden)
            self._thread.join(timeout=2.0)
            
            # Falls Thread noch läuft: Force-Kill (letzter Ausweg)
            if self._thread.is_alive():
                # Thread ist noch aktiv - das sollte nicht passieren, aber sicherheitshalber
                import sys
                import traceback
                print("WARNUNG: Thread konnte nicht sauber beendet werden!", file=sys.stderr)
                traceback.print_exc()
                # Thread-Referenz löschen - wird beim nächsten Start neu erstellt
                self._thread = None

    def _click_loop(self):
        """Haupt-Loop im Thread - führt die Clicks aus."""
        click_count = 0
        target_pos = self._target_position if self._target_position is not None else self._current_position

        try:
            while not self._stop_event.is_set():
                # Prüfen ob gestoppt werden soll (vor jedem Click)
                if self._stop_event.is_set():
                    break
                
                # Click ausführen
                try:
                    self._mouse_controller.click(
                        button=self._mouse_button,
                        click_type=self._click_type,
                        position=target_pos
                    )
                except Exception:
                    # Bei Fehler beim Click: trotzdem weitermachen, aber prüfen ob gestoppt
                    if self._stop_event.is_set():
                        break
                    continue

                # Callback aufrufen
                if self._on_click_callback:
                    try:
                        self._on_click_callback(click_count + 1)
                    except Exception:
                        pass  # Callback-Fehler ignorieren

                click_count += 1

                # Prüfen ob Wiederholungsanzahl erreicht
                if self._repeat_count > 0 and click_count >= self._repeat_count:
                    break
                
                # Nochmal prüfen ob gestoppt werden soll (nach Click, vor Wartezeit)
                if self._stop_event.is_set():
                    break

                # Warten auf nächstes Intervall
                interval_seconds = self._interval.total_seconds()
                if interval_seconds > 0:
                    # In sehr kleine Schritte aufteilen für sofortiges Stoppen
                    elapsed = 0.0
                    step = 0.05  # 50ms Schritte für sehr responsives Stoppen
                    while elapsed < interval_seconds and not self._stop_event.is_set():
                        sleep_time = min(step, interval_seconds - elapsed)
                        time.sleep(sleep_time)
                        elapsed += step
                        
                        # Zusätzliche Prüfung nach jedem Schritt
                        if self._stop_event.is_set():
                            break

        finally:
            self._is_running = False
            # Finished-Callback aufrufen
            if self._on_finished_callback:
                try:
                    self._on_finished_callback()
                except Exception:
                    pass  # Callback-Fehler ignorieren


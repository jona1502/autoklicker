"""RecorderService - Click-Events aufzeichnen und abspielen."""
import time
import threading
from datetime import datetime
from typing import List, Optional, Callable

from src.core.mouse_controller import MouseController
from src.models.click_event import ClickEvent


class RecorderService:
    """Service für das Aufzeichnen und Abspielen von Click-Sequenzen."""

    def __init__(self, mouse_controller: MouseController):
        """
        Initialisiert den RecorderService.

        Args:
            mouse_controller: MouseController Instanz
        """
        self._mouse_controller = mouse_controller
        self._is_recording = False
        self._is_playing = False
        self._recorded_events: List[ClickEvent] = []
        self._recording_start_time: Optional[float] = None
        self._last_event_time: Optional[float] = None
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_playback_event = threading.Event()

        # Callbacks
        self._on_record_callback: Optional[Callable[[int], None]] = None
        self._on_playback_callback: Optional[Callable[[int, int], None]] = None  # (current, total)
        self._on_finished_callback: Optional[Callable] = None

    @property
    def is_recording(self) -> bool:
        """Gibt zurück, ob gerade aufgezeichnet wird."""
        return self._is_recording

    @property
    def is_playing(self) -> bool:
        """Gibt zurück, ob gerade abgespielt wird."""
        return self._is_playing

    @property
    def recorded_events(self) -> List[ClickEvent]:
        """Gibt die aufgezeichneten Events zurück."""
        return self._recorded_events.copy()

    def set_on_record_callback(self, callback: Optional[Callable[[int], None]]):
        """Setzt einen Callback, der bei jedem aufgezeichneten Event aufgerufen wird."""
        self._on_record_callback = callback

    def set_on_playback_callback(self, callback: Optional[Callable[[int, int], None]]):
        """Setzt einen Callback, der während des Abspielens aufgerufen wird (current, total)."""
        self._on_playback_callback = callback

    def set_on_finished_callback(self, callback: Optional[Callable]):
        """Setzt einen Callback, der aufgerufen wird, wenn das Abspielen beendet ist."""
        self._on_finished_callback = callback

    def start_recording(self):
        """Startet die Aufzeichnung."""
        if self._is_recording:
            return

        self._is_recording = True
        self._recorded_events.clear()
        self._recording_start_time = time.time()
        self._last_event_time = self._recording_start_time

    def stop_recording(self) -> List[ClickEvent]:
        """
        Stoppt die Aufzeichnung und gibt die Events zurück.

        Returns:
            Liste der aufgezeichneten ClickEvent Objekte
        """
        if not self._is_recording:
            return []

        self._is_recording = False
        return self._recorded_events.copy()

    def record_click(self, position: tuple[int, int], button: str, click_type: str):
        """
        Zeichnet einen Click-Event auf.

        Args:
            position: Tuple (x, y)
            button: "left", "right" oder "middle"
            click_type: "single", "double" oder "triple"
        """
        if not self._is_recording:
            return

        current_time = time.time()
        delay = 0.0

        if self._last_event_time is not None:
            delay = current_time - self._last_event_time

        event = ClickEvent(
            position=position,
            button=button,
            click_type=click_type,
            timestamp=datetime.now(),
            delay_from_previous=delay
        )

        self._recorded_events.append(event)
        self._last_event_time = current_time

        # Callback aufrufen
        if self._on_record_callback:
            try:
                self._on_record_callback(len(self._recorded_events))
            except Exception:
                pass

    def playback(self, events: Optional[List[ClickEvent]] = None, repeat: bool = False):
        """
        Spielt eine Sequenz von Click-Events ab.

        Args:
            events: Liste der ClickEvent Objekte. Wenn None, werden die aufgezeichneten Events verwendet.
            repeat: Wenn True, wird die Sequenz wiederholt bis gestoppt wird.
        """
        if self._is_playing:
            return

        if events is None:
            events = self._recorded_events.copy()

        if not events:
            return

        self._stop_playback_event.clear()
        self._is_playing = True
        self._playback_thread = threading.Thread(
            target=self._playback_loop,
            args=(events, repeat),
            daemon=True
        )
        self._playback_thread.start()

    def stop_playback(self):
        """Stoppt das Abspielen."""
        if not self._is_playing:
            return

        self._stop_playback_event.set()
        self._is_playing = False

        if self._playback_thread is not None and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=1.0)

    def _playback_loop(self, events: List[ClickEvent], repeat: bool):
        """Haupt-Loop für das Abspielen."""
        try:
            while not self._stop_playback_event.is_set():
                for i, event in enumerate(events):
                    if self._stop_playback_event.is_set():
                        break

                    # Click ausführen
                    self._mouse_controller.click(
                        button=event.button,
                        click_type=event.click_type,
                        position=event.position
                    )

                    # Callback aufrufen
                    if self._on_playback_callback:
                        try:
                            self._on_playback_callback(i + 1, len(events))
                        except Exception:
                            pass

                    # Warten auf nächstes Event (außer beim letzten Event wenn nicht wiederholt)
                    if i < len(events) - 1:
                        # Delay bis zum nächsten Event
                        next_event = events[i + 1]
                        delay = next_event.delay_from_previous
                    elif repeat:
                        # Wenn wiederholt wird, Delay bis zum ersten Event
                        delay = events[0].delay_from_previous if len(events) > 0 else 0.0
                    else:
                        # Letztes Event, kein Delay
                        delay = 0.0

                    if delay > 0:
                        # In kleine Schritte aufteilen für responsives Stoppen
                        elapsed = 0.0
                        step = min(0.1, delay / 10)
                        while elapsed < delay and not self._stop_playback_event.is_set():
                            time.sleep(min(step, delay - elapsed))
                            elapsed += step

                if not repeat:
                    break

        finally:
            self._is_playing = False
            # Finished-Callback aufrufen
            if self._on_finished_callback:
                try:
                    self._on_finished_callback()
                except Exception:
                    pass

    def clear_events(self):
        """Löscht alle aufgezeichneten Events."""
        self._recorded_events.clear()


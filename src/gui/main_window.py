"""MainWindow - Hauptfenster der Anwendung."""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from src.core.clicker import ClickerEngine
from src.core.mouse_controller import MouseController
from src.core.hotkey_manager import HotkeyManager
from src.services.recorder import RecorderService
from src.services.settings_manager import SettingsManager
from src.models.settings import AppSettings
from src.utils.validators import validate_interval_component
from src.gui.hotkey_dialog import HotkeyDialog
from src.gui.record_window import RecordWindow


class MainWindow:
    """Hauptfenster der AutoKlicker-Anwendung."""

    def __init__(self, root: tk.Tk):
        """
        Initialisiert das Hauptfenster.

        Args:
            root: Tkinter Root-Window
        """
        self.root = root
        self.root.title("OP Auto Clicker 3.0")
        self.root.geometry("500x450")
        self.root.resizable(True, True)

        # Services initialisieren
        self._mouse_controller = MouseController()
        self._clicker_engine = ClickerEngine(self._mouse_controller)
        self._hotkey_manager = HotkeyManager()
        self._recorder_service = RecorderService(self._mouse_controller)
        self._settings_manager = SettingsManager()
        self._settings: Optional[AppSettings] = None

        # UI-Variablen
        self._create_variables()
        
        # GUI erstellen
        self._create_widgets()
        
        # Callbacks setzen
        self._setup_callbacks()
        
        # Settings laden
        self._load_settings()
        
        # Hotkeys registrieren
        self._register_hotkeys()

    def _create_variables(self):
        """Erstellt Tkinter-Variablen für die UI-Elemente."""
        # Click Interval
        self.var_hours = tk.StringVar(value="0")
        self.var_minutes = tk.StringVar(value="0")
        self.var_seconds = tk.StringVar(value="30")
        self.var_milliseconds = tk.StringVar(value="100")

        # Click Options
        self.var_mouse_button = tk.StringVar(value="Left")
        self.var_click_type = tk.StringVar(value="Single")

        # Click Repeat
        self.var_repeat_mode = tk.StringVar(value="until_stopped")
        self.var_repeat_count = tk.StringVar(value="1")

        # Cursor Position
        self.var_position_mode = tk.StringVar(value="current")
        self.var_pick_x = tk.StringVar(value="0")
        self.var_pick_y = tk.StringVar(value="0")

    def _create_widgets(self):
        """Erstellt alle UI-Widgets."""
        # Click Interval Section
        interval_frame = ttk.LabelFrame(self.root, text="Click interval", padding=10)
        interval_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)

        ttk.Label(interval_frame, text="0").grid(row=0, column=0)
        self.entry_hours = ttk.Entry(interval_frame, textvariable=self.var_hours, width=5)
        self.entry_hours.grid(row=0, column=1, padx=2)
        ttk.Label(interval_frame, text="hours").grid(row=0, column=2, padx=5)

        ttk.Label(interval_frame, text="0").grid(row=0, column=3)
        self.entry_minutes = ttk.Entry(interval_frame, textvariable=self.var_minutes, width=5)
        self.entry_minutes.grid(row=0, column=4, padx=2)
        ttk.Label(interval_frame, text="mins").grid(row=0, column=5, padx=5)

        ttk.Label(interval_frame, text="30").grid(row=0, column=6)
        self.entry_seconds = ttk.Entry(interval_frame, textvariable=self.var_seconds, width=5)
        self.entry_seconds.grid(row=0, column=7, padx=2)
        ttk.Label(interval_frame, text="secs").grid(row=0, column=8, padx=5)

        ttk.Label(interval_frame, text="100").grid(row=0, column=9)
        self.entry_milliseconds = ttk.Entry(interval_frame, textvariable=self.var_milliseconds, width=5)
        self.entry_milliseconds.grid(row=0, column=10, padx=2)
        ttk.Label(interval_frame, text="milliseconds").grid(row=0, column=11, padx=5)

        # Click Options Section
        options_frame = ttk.LabelFrame(self.root, text="Click options", padding=10)
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        ttk.Label(options_frame, text="Mouse button:").grid(row=0, column=0, sticky=tk.W, pady=5)
        combo_mouse_button = ttk.Combobox(options_frame, textvariable=self.var_mouse_button, 
                                         values=["Left", "Right", "Middle"], state="readonly", width=15)
        combo_mouse_button.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(options_frame, text="Click type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        combo_click_type = ttk.Combobox(options_frame, textvariable=self.var_click_type,
                                       values=["Single", "Double", "Triple"], state="readonly", width=15)
        combo_click_type.grid(row=1, column=1, padx=5, pady=5)

        # Click Repeat Section
        repeat_frame = ttk.LabelFrame(self.root, text="Click repeat", padding=10)
        repeat_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.radio_repeat = ttk.Radiobutton(repeat_frame, text="Repeat", variable=self.var_repeat_mode,
                                            value="repeat")
        self.radio_repeat.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.spinbox_repeat = ttk.Spinbox(repeat_frame, from_=1, to=999999, textvariable=self.var_repeat_count,
                                         width=10, state="disabled")
        self.spinbox_repeat.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(repeat_frame, text="times").grid(row=0, column=2, sticky=tk.W, pady=5)

        self.radio_until_stopped = ttk.Radiobutton(repeat_frame, text="Repeat until stopped",
                                                   variable=self.var_repeat_mode, value="until_stopped")
        self.radio_until_stopped.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Cursor Position Section
        position_frame = ttk.LabelFrame(self.root, text="Cursor position", padding=10)
        position_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.radio_current = ttk.Radiobutton(position_frame, text="Current location",
                                            variable=self.var_position_mode, value="current",
                                            command=self._on_position_mode_changed)
        self.radio_current.grid(row=0, column=0, sticky=tk.W, pady=5)

        self.radio_pick = ttk.Radiobutton(position_frame, text="Pick location",
                                         variable=self.var_position_mode, value="pick",
                                         command=self._on_position_mode_changed)
        self.radio_pick.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.btn_pick_location = ttk.Button(position_frame, text="Pick location", command=self._pick_location,
                                           state="disabled")
        self.btn_pick_location.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(position_frame, text="X").grid(row=1, column=2, padx=5)
        self.entry_pick_x = ttk.Entry(position_frame, textvariable=self.var_pick_x, width=8, state="disabled")
        self.entry_pick_x.grid(row=1, column=3, padx=2)

        ttk.Label(position_frame, text="Y").grid(row=1, column=4, padx=5)
        self.entry_pick_y = ttk.Entry(position_frame, textvariable=self.var_pick_y, width=8, state="disabled")
        self.entry_pick_y.grid(row=1, column=5, padx=2)

        # Action Buttons
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=20)

        hotkey_str = self._hotkey_manager.get_start_hotkey_string().upper()
        self.btn_start = ttk.Button(buttons_frame, text=f"Start ({hotkey_str})", command=self._start_clicking,
                                    width=20)
        self.btn_start.grid(row=0, column=0, padx=5, pady=5)

        self.btn_stop = ttk.Button(buttons_frame, text=f"Stop ({hotkey_str})", command=self._stop_clicking,
                                   width=20, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=5, pady=5)

        self.btn_hotkey = ttk.Button(buttons_frame, text="Hotkey setting", command=self._open_hotkey_dialog,
                                     width=20)
        self.btn_hotkey.grid(row=1, column=0, padx=5, pady=5)

        self.btn_record = ttk.Button(buttons_frame, text="Record & Playback", command=self._open_record_window,
                                     width=20)
        self.btn_record.grid(row=1, column=1, padx=5, pady=5)

        # Grid weights für Resizing
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

    def _setup_callbacks(self):
        """Richtet Callbacks für die Services ein."""
        # ClickerEngine Callbacks
        self._clicker_engine.set_on_finished_callback(self._on_clicking_finished)
        
        # Repeat Mode ändern
        self.var_repeat_mode.trace_add("write", lambda *args: self._on_repeat_mode_changed())

    def _on_repeat_mode_changed(self):
        """Wird aufgerufen wenn der Repeat-Mode geändert wird."""
        if self.var_repeat_mode.get() == "repeat":
            self.spinbox_repeat.config(state="normal")
        else:
            self.spinbox_repeat.config(state="disabled")

    def _on_position_mode_changed(self):
        """Wird aufgerufen wenn der Position-Mode geändert wird."""
        if self.var_position_mode.get() == "pick":
            self.btn_pick_location.config(state="normal")
            self.entry_pick_x.config(state="normal")
            self.entry_pick_y.config(state="normal")
        else:
            self.btn_pick_location.config(state="disabled")
            self.entry_pick_x.config(state="disabled")
            self.entry_pick_y.config(state="disabled")

    def _pick_location(self):
        """Öffnet den Location-Picker."""
        # Info-Dialog anzeigen
        messagebox.showinfo("Pick Location", 
                          "Klicken Sie auf die gewünschte Position auf dem Bildschirm.\n"
                          "Das Fenster wird kurz ausgeblendet.")
        
        # Fenster kurz verstecken (damit User auf Desktop klicken kann)
        self.root.withdraw()
        self.root.update()
        
        def pick_in_thread():
            try:
                position = self._mouse_controller.pick_location()
                if position:
                    self.root.after(0, lambda: self._on_location_picked(position))
                else:
                    self.root.after(0, self.root.deiconify)
            except Exception as e:
                self.root.after(0, lambda: self._on_pick_error(str(e)))
        
        thread = threading.Thread(target=pick_in_thread, daemon=True)
        thread.start()

    def _on_location_picked(self, position: tuple[int, int]):
        """Wird aufgerufen wenn eine Position ausgewählt wurde."""
        x, y = position
        self.var_pick_x.set(str(x))
        self.var_pick_y.set(str(y))
        self.root.deiconify()  # Fenster wieder anzeigen
        messagebox.showinfo("Position ausgewählt", f"Position gesetzt: X={x}, Y={y}")

    def _on_pick_error(self, error: str):
        """Wird aufgerufen wenn ein Fehler beim Pick Location auftritt."""
        self.root.deiconify()
        messagebox.showerror("Fehler", f"Fehler beim Auswählen der Position: {error}")

    def _start_clicking(self):
        """Startet das automatische Klicken."""
        # Validierung
        if not self._validate_inputs():
            return

        # Parameter aus UI lesen
        hours = validate_interval_component(self.var_hours.get(), "hours")
        minutes = validate_interval_component(self.var_minutes.get(), "minutes")
        seconds = validate_interval_component(self.var_seconds.get(), "seconds")
        milliseconds = validate_interval_component(self.var_milliseconds.get(), "milliseconds")

        # ClickerEngine konfigurieren
        self._clicker_engine.set_interval_from_components(hours, minutes, seconds, milliseconds)
        self._clicker_engine.mouse_button = self.var_mouse_button.get().lower()
        self._clicker_engine.click_type = self.var_click_type.get().lower()

        # Repeat-Mode
        if self.var_repeat_mode.get() == "repeat":
            try:
                count = int(self.var_repeat_count.get())
                self._clicker_engine.repeat_count = max(1, count)
            except ValueError:
                self._clicker_engine.repeat_count = 1
        else:
            self._clicker_engine.repeat_count = -1  # Unendlich

        # Position
        if self.var_position_mode.get() == "pick":
            try:
                x = int(self.var_pick_x.get())
                y = int(self.var_pick_y.get())
                self._clicker_engine.target_position = (x, y)
            except ValueError:
                messagebox.showerror("Fehler", "Ungültige Koordinaten!")
                return
        else:
            self._clicker_engine.target_position = None  # Aktuelle Position

        # Starten
        self._clicker_engine.start()
        self._update_ui_state(running=True)

    def _stop_clicking(self):
        """Stoppt das automatische Klicken."""
        self._clicker_engine.stop()
        self._update_ui_state(running=False)

    def _on_clicking_finished(self):
        """Wird aufgerufen wenn das Klicken beendet ist."""
        self.root.after(0, lambda: self._update_ui_state(running=False))

    def _update_ui_state(self, running: bool):
        """Aktualisiert den UI-Status."""
        if running:
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            # UI-Elemente deaktivieren während des Klickens
            for widget in [self.entry_hours, self.entry_minutes, self.entry_seconds, self.entry_milliseconds,
                          self.radio_repeat, self.radio_until_stopped, self.spinbox_repeat,
                          self.radio_current, self.radio_pick, self.btn_pick_location]:
                try:
                    widget.config(state="disabled")
                except:
                    pass
        else:
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            # UI-Elemente wieder aktivieren
            for widget in [self.entry_hours, self.entry_minutes, self.entry_seconds, self.entry_milliseconds]:
                widget.config(state="normal")
            # Repeat-Mode wiederherstellen
            self._on_repeat_mode_changed()
            # Position-Mode wiederherstellen
            self._on_position_mode_changed()

    def _validate_inputs(self) -> bool:
        """Validiert alle Eingaben."""
        try:
            # Intervall-Komponenten validieren
            hours = validate_interval_component(self.var_hours.get(), "hours")
            minutes = validate_interval_component(self.var_minutes.get(), "minutes")
            seconds = validate_interval_component(self.var_seconds.get(), "seconds")
            milliseconds = validate_interval_component(self.var_milliseconds.get(), "milliseconds")

            # Mindestens 1ms Intervall
            total_ms = (hours * 3600000) + (minutes * 60000) + (seconds * 1000) + milliseconds
            if total_ms < 1:
                messagebox.showerror("Fehler", "Das Intervall muss mindestens 1 Millisekunde betragen!")
                return False

            # Position validieren wenn "Pick location" ausgewählt
            if self.var_position_mode.get() == "pick":
                try:
                    x = int(self.var_pick_x.get())
                    y = int(self.var_pick_y.get())
                    if x < 0 or y < 0:
                        messagebox.showerror("Fehler", "Koordinaten müssen positiv sein!")
                        return False
                except ValueError:
                    messagebox.showerror("Fehler", "Ungültige Koordinaten!")
                    return False

            return True
        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültige Eingabe: {e}")
            return False

    def _register_hotkeys(self):
        """Registriert die Hotkeys."""
        def toggle_clicking():
            if self._clicker_engine.is_running:
                self._stop_clicking()
            else:
                self._start_clicking()

        self._hotkey_manager.set_start_hotkey("f6", None, toggle_clicking)
        self._hotkey_manager.set_stop_hotkey("f6", None, toggle_clicking)

    def _open_hotkey_dialog(self):
        """Öffnet den Hotkey-Settings Dialog."""
        def on_save(start_key: str, stop_key: str, modifiers: Optional[list]):
            def toggle_clicking():
                if self._clicker_engine.is_running:
                    self._stop_clicking()
                else:
                    self._start_clicking()

            # Hotkeys aktualisieren
            self._hotkey_manager.unregister_all()
            self._hotkey_manager.set_start_hotkey(start_key, modifiers, toggle_clicking)
            self._hotkey_manager.set_stop_hotkey(stop_key, modifiers, toggle_clicking)

            # UI aktualisieren
            hotkey_str = self._hotkey_manager.get_start_hotkey_string().upper()
            self.btn_start.config(text=f"Start ({hotkey_str})")
            self.btn_stop.config(text=f"Stop ({hotkey_str})")

            # Settings speichern
            if self._settings:
                self._settings.start_hotkey = start_key
                self._settings.stop_hotkey = stop_key
                self._settings.hotkey_modifiers = modifiers if modifiers else []
                self._settings_manager.save_settings(self._settings)

        dialog = HotkeyDialog(self.root, self._hotkey_manager, on_save)

    def _open_record_window(self):
        """Öffnet das Record & Playback Fenster."""
        RecordWindow(self.root, self._recorder_service)

    def _load_settings(self):
        """Lädt die Einstellungen."""
        self._settings = self._settings_manager.load_settings()
        
        # UI mit Settings füllen
        if self._settings:
            self.var_hours.set(str(self._settings.default_hours))
            self.var_minutes.set(str(self._settings.default_minutes))
            self.var_seconds.set(str(self._settings.default_seconds))
            self.var_milliseconds.set(str(self._settings.default_milliseconds))
            self.var_mouse_button.set(self._settings.default_mouse_button.capitalize())
            self.var_click_type.set(self._settings.default_click_type.capitalize())
            self.var_repeat_count.set(str(self._settings.default_repeat_count))
            self.var_repeat_mode.set("until_stopped" if self._settings.default_repeat_until_stopped else "repeat")
            self.var_position_mode.set("current" if self._settings.default_use_current_location else "pick")
            self.var_pick_x.set(str(self._settings.default_pick_x))
            self.var_pick_y.set(str(self._settings.default_pick_y))
            self._on_position_mode_changed()
            self._on_repeat_mode_changed()

    def _save_settings(self):
        """Speichert die Einstellungen."""
        if not self._settings:
            self._settings = AppSettings()

        # UI-Werte in Settings speichern
        try:
            self._settings.default_hours = validate_interval_component(self.var_hours.get(), "hours")
            self._settings.default_minutes = validate_interval_component(self.var_minutes.get(), "minutes")
            self._settings.default_seconds = validate_interval_component(self.var_seconds.get(), "seconds")
            self._settings.default_milliseconds = validate_interval_component(self.var_milliseconds.get(), "milliseconds")
            self._settings.default_mouse_button = self.var_mouse_button.get().lower()
            self._settings.default_click_type = self.var_click_type.get().lower()
            self._settings.default_repeat_count = int(self.var_repeat_count.get())
            self._settings.default_repeat_until_stopped = (self.var_repeat_mode.get() == "until_stopped")
            self._settings.default_use_current_location = (self.var_position_mode.get() == "current")
            self._settings.default_pick_x = int(self.var_pick_x.get())
            self._settings.default_pick_y = int(self.var_pick_y.get())

            self._settings_manager.save_settings(self._settings)
        except Exception as e:
            print(f"Fehler beim Speichern der Settings: {e}")

    def on_closing(self):
        """Wird aufgerufen wenn das Fenster geschlossen wird."""
        # Clicker stoppen
        if self._clicker_engine.is_running:
            self._clicker_engine.stop()

        # Hotkeys entfernen
        self._hotkey_manager.unregister_all()

        # Settings speichern
        self._save_settings()

        # Fenster schließen
        self.root.destroy()


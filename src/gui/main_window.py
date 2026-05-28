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
from src.gui.theme import APP_NAME, APP_VERSION, COLORS, apply_theme


class MainWindow:
    """Hauptfenster der AutoKlicker-Anwendung."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("560x640")
        self.root.minsize(520, 600)
        self.root.resizable(True, True)
        apply_theme(self.root)

        try:
            import os
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "icons",
                "mauszeiger.ico",
            )
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self._mouse_controller = MouseController()
        self._clicker_engine = ClickerEngine(self._mouse_controller)
        self._hotkey_manager = HotkeyManager()
        self._recorder_service = RecorderService(self._mouse_controller)
        self._settings_manager = SettingsManager()
        self._settings: Optional[AppSettings] = None

        self._create_variables()
        self._create_widgets()
        self._setup_callbacks()
        self._load_settings()
        self._register_hotkeys()

    def _create_variables(self):
        self.var_hours = tk.StringVar(value="0")
        self.var_minutes = tk.StringVar(value="0")
        self.var_seconds = tk.StringVar(value="1")
        self.var_milliseconds = tk.StringVar(value="0")
        self.var_mouse_button = tk.StringVar(value="Left")
        self.var_click_type = tk.StringVar(value="Single")
        self.var_repeat_mode = tk.StringVar(value="until_stopped")
        self.var_repeat_count = tk.StringVar(value="1")
        self.var_position_mode = tk.StringVar(value="current")
        self.var_pick_x = tk.StringVar(value="0")
        self.var_pick_y = tk.StringVar(value="0")
        self.var_status = tk.StringVar(value="Bereit")
        self.var_start_summary = tk.StringVar(value="F6")
        self.var_stop_summary = tk.StringVar(value="F7")
        self.var_position_summary = tk.StringVar(value="Aktuelle Position")

    def _create_widgets(self):
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container, style="Surface.TFrame", padding=(14, 12))
        header.pack(fill=tk.X, pady=(0, 12))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)
        ttk.Label(header, text=APP_NAME, style="HeaderTitle.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(
            header,
            text=f"Version {APP_VERSION}  |  Praezise Klicks, Hotkeys und Aufnahmen",
            style="HeaderSubtitle.TLabel",
        ).grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        status_badge = ttk.Frame(header, style="Toolbar.TFrame", padding=(12, 8))
        status_badge.grid(row=0, column=1, rowspan=2, sticky=tk.E)
        ttk.Label(status_badge, text="Status", style="Toolbar.TLabel").pack(anchor=tk.E)
        self.label_status = ttk.Label(status_badge, textvariable=self.var_status, style="Toolbar.TLabel")
        self.label_status.pack(anchor=tk.E)

        quick_frame = ttk.Frame(container)
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        quick_frame.columnconfigure(0, weight=1)
        quick_frame.columnconfigure(1, weight=1)
        quick_frame.columnconfigure(2, weight=1)
        self._create_summary_tile(quick_frame, "Start", self.var_start_summary, 0)
        self._create_summary_tile(quick_frame, "Stopp", self.var_stop_summary, 1)
        self._create_summary_tile(quick_frame, "Modus", self.var_position_summary, 2)

        interval_frame = ttk.LabelFrame(container, text=" Klick-Intervall ", padding=14)
        interval_frame.pack(fill=tk.X, pady=(0, 10))

        interval_grid = ttk.Frame(interval_frame)
        interval_grid.pack(fill=tk.X)
        for col in range(4):
            interval_grid.columnconfigure(col, weight=1, uniform="interval")

        fields = [
            (self.var_hours, "Std"),
            (self.var_minutes, "Min"),
            (self.var_seconds, "Sek"),
            (self.var_milliseconds, "ms"),
        ]
        self._interval_entries = []
        for col, (var, unit) in enumerate(fields):
            cell = ttk.Frame(interval_grid)
            cell.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0), sticky=tk.EW)
            ttk.Label(cell, text=unit, style="Muted.TLabel").pack(anchor=tk.W, pady=(0, 4))
            entry = ttk.Entry(cell, textvariable=var, width=8, justify="center")
            entry.pack(fill=tk.X)
            self._interval_entries.append(entry)

        mid_row = ttk.Frame(container)
        mid_row.pack(fill=tk.X, pady=(0, 10))
        mid_row.columnconfigure(0, weight=1)
        mid_row.columnconfigure(1, weight=1)

        options_frame = ttk.LabelFrame(mid_row, text=" Klick-Optionen ", padding=14)
        options_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(0, 6))

        ttk.Label(options_frame, text="Maus-Taste", style="Muted.TLabel").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(
            options_frame,
            textvariable=self.var_mouse_button,
            values=["Left", "Right", "Middle"],
            state="readonly",
            width=14,
        ).grid(row=0, column=1, padx=(10, 0), pady=5, sticky=tk.EW)

        ttk.Label(options_frame, text="Klick-Typ", style="Muted.TLabel").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(
            options_frame,
            textvariable=self.var_click_type,
            values=["Single", "Double", "Triple"],
            state="readonly",
            width=14,
        ).grid(row=1, column=1, padx=(10, 0), pady=5, sticky=tk.EW)
        options_frame.columnconfigure(1, weight=1)

        repeat_frame = ttk.LabelFrame(mid_row, text=" Wiederholung ", padding=14)
        repeat_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(6, 0))

        self.radio_repeat = ttk.Radiobutton(
            repeat_frame, text="Anzahl:", variable=self.var_repeat_mode, value="repeat"
        )
        self.radio_repeat.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.spinbox_repeat = ttk.Spinbox(
            repeat_frame,
            from_=1,
            to=999999,
            textvariable=self.var_repeat_count,
            width=8,
            state="disabled",
        )
        self.spinbox_repeat.grid(row=0, column=1, padx=8, pady=5, sticky=tk.EW)
        ttk.Label(repeat_frame, text="mal", style="Muted.TLabel").grid(row=0, column=2, sticky=tk.W)

        self.radio_until_stopped = ttk.Radiobutton(
            repeat_frame,
            text="Bis zum Stopp",
            variable=self.var_repeat_mode,
            value="until_stopped",
        )
        self.radio_until_stopped.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        repeat_frame.columnconfigure(1, weight=1)

        position_frame = ttk.LabelFrame(container, text=" Cursor-Position ", padding=14)
        position_frame.pack(fill=tk.X, pady=(0, 10))
        position_frame.columnconfigure(2, weight=1)

        self.radio_current = ttk.Radiobutton(
            position_frame,
            text="Aktuelle Position beim Start",
            variable=self.var_position_mode,
            value="current",
            command=self._on_position_mode_changed,
        )
        self.radio_current.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=5)

        self.radio_pick = ttk.Radiobutton(
            position_frame,
            text="Feste Position",
            variable=self.var_position_mode,
            value="pick",
            command=self._on_position_mode_changed,
        )
        self.radio_pick.grid(row=1, column=0, sticky=tk.W, pady=5)

        self.btn_pick_location = ttk.Button(
            position_frame, text="Position wählen", command=self._pick_location, state="disabled"
        )
        self.btn_pick_location.grid(row=1, column=1, padx=10, pady=5)

        coord_frame = ttk.Frame(position_frame)
        coord_frame.grid(row=1, column=2, columnspan=2, sticky=tk.E)
        ttk.Label(coord_frame, text="X", style="Muted.TLabel").pack(side=tk.LEFT)
        self.entry_pick_x = ttk.Entry(coord_frame, textvariable=self.var_pick_x, width=7, state="disabled")
        self.entry_pick_x.pack(side=tk.LEFT, padx=4)
        ttk.Label(coord_frame, text="Y", style="Muted.TLabel").pack(side=tk.LEFT)
        self.entry_pick_y = ttk.Entry(coord_frame, textvariable=self.var_pick_y, width=7, state="disabled")
        self.entry_pick_y.pack(side=tk.LEFT, padx=4)

        actions_frame = ttk.Frame(container, style="Surface.TFrame", padding=14)
        actions_frame.pack(fill=tk.X, pady=(0, 10))

        btn_row = ttk.Frame(actions_frame)
        btn_row.pack(fill=tk.X)
        btn_row.columnconfigure(0, weight=1)
        btn_row.columnconfigure(1, weight=1)

        self.btn_start = ttk.Button(
            btn_row, text="Start (F6)", command=self._start_clicking, style="Success.TButton"
        )
        self.btn_start.grid(row=0, column=0, sticky=tk.EW, padx=(0, 6), pady=(0, 8))

        self.btn_stop = ttk.Button(
            btn_row,
            text="Stopp (F7)",
            command=self._stop_clicking,
            style="Danger.TButton",
            state="disabled",
        )
        self.btn_stop.grid(row=0, column=1, sticky=tk.EW, padx=(6, 0), pady=(0, 8))

        btn_row2 = ttk.Frame(actions_frame)
        btn_row2.pack(fill=tk.X)
        btn_row2.columnconfigure(0, weight=1)
        btn_row2.columnconfigure(1, weight=1)

        self.btn_hotkey = ttk.Button(btn_row2, text="Hotkeys", command=self._open_hotkey_dialog)
        self.btn_hotkey.grid(row=0, column=0, sticky=tk.EW, padx=(0, 6))

        self.btn_record = ttk.Button(btn_row2, text="Aufnahme & Wiedergabe", command=self._open_record_window)
        self.btn_record.grid(row=0, column=1, sticky=tk.EW, padx=(6, 0))

        ttk.Label(
            actions_frame,
            text="F6 = Start   |   F7 = Stopp (Notfall)",
            style="Hotkey.TLabel",
        ).pack(anchor=tk.W, pady=(10, 0))

        footer = ttk.Frame(container)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(12, 0))
        ttk.Separator(footer).pack(fill=tk.X, pady=(0, 6))
        ttk.Label(footer, text="Einstellungen werden beim Schliessen automatisch gespeichert.", style="Status.TLabel").pack(
            anchor=tk.W
        )

        self.entry_hours = self._interval_entries[0]
        self.entry_minutes = self._interval_entries[1]
        self.entry_seconds = self._interval_entries[2]
        self.entry_milliseconds = self._interval_entries[3]

    def _create_summary_tile(self, parent: ttk.Frame, label: str, value: tk.StringVar, column: int):
        tile = ttk.Frame(parent, style="Surface.TFrame", padding=(12, 10))
        tile.grid(row=0, column=column, sticky=tk.EW, padx=(0 if column == 0 else 8, 0))
        ttk.Label(tile, text=label, style="SurfaceMuted.TLabel").pack(anchor=tk.W)
        ttk.Label(tile, textvariable=value, style="Kpi.TLabel").pack(anchor=tk.W, pady=(2, 0))

    def _setup_callbacks(self):
        self._clicker_engine.set_on_finished_callback(self._on_clicking_finished)
        self.var_repeat_mode.trace_add("write", lambda *args: self._on_repeat_mode_changed())

    def _on_repeat_mode_changed(self):
        if self.var_repeat_mode.get() == "repeat":
            self.spinbox_repeat.config(state="normal")
        else:
            self.spinbox_repeat.config(state="disabled")

    def _on_position_mode_changed(self):
        if self.var_position_mode.get() == "pick":
            self.var_position_summary.set("Feste Position")
            self.btn_pick_location.config(state="normal")
            self.entry_pick_x.config(state="normal")
            self.entry_pick_y.config(state="normal")
        else:
            self.var_position_summary.set("Aktuelle Position")
            self.btn_pick_location.config(state="disabled")
            self.entry_pick_x.config(state="disabled")
            self.entry_pick_y.config(state="disabled")

    def _pick_location(self):
        self.root.withdraw()
        self.root.update()

        overlay = tk.Toplevel(self.root)
        overlay.attributes("-alpha", 0.35)
        overlay.attributes("-topmost", True)
        overlay.attributes("-fullscreen", True)
        overlay.configure(bg="black")

        label = tk.Label(
            overlay,
            text="Linksklick an gewünschter Position\n\nESC zum Abbrechen",
            font=("Segoe UI", 22, "bold"),
            fg=COLORS["text"],
            bg="black",
        )
        label.place(relx=0.5, rely=0.5, anchor="center")

        cancelled = [False]

        def on_escape(event):
            cancelled[0] = True
            overlay.destroy()
            self.root.deiconify()

        overlay.bind("<Escape>", on_escape)
        overlay.update()

        def pick_in_thread():
            try:
                import time

                time.sleep(0.2)
                position = self._mouse_controller.pick_location()
                self.root.after(0, overlay.destroy)

                if position and not cancelled[0]:
                    self.root.after(0, lambda pos=position: self._on_location_picked(pos))
                else:
                    self.root.after(0, self.root.deiconify)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, overlay.destroy)
                self.root.after(0, lambda err=error_msg: self._on_pick_error(err))

        thread = threading.Thread(target=pick_in_thread, daemon=True)
        thread.start()

    def _on_location_picked(self, position: tuple[int, int]):
        x, y = position
        self.var_pick_x.set(str(x))
        self.var_pick_y.set(str(y))
        self.root.deiconify()
        messagebox.showinfo("Position", f"Position gesetzt:\nX = {x}\nY = {y}")

    def _on_pick_error(self, error: str):
        self.root.deiconify()
        messagebox.showerror("Fehler", f"Fehler beim Auswählen der Position: {error}")

    def _start_clicking(self):
        if not self._validate_inputs():
            return

        hours = validate_interval_component(self.var_hours.get(), "hours")
        minutes = validate_interval_component(self.var_minutes.get(), "minutes")
        seconds = validate_interval_component(self.var_seconds.get(), "seconds")
        milliseconds = validate_interval_component(self.var_milliseconds.get(), "milliseconds")

        self._clicker_engine.set_interval_from_components(hours, minutes, seconds, milliseconds)
        self._clicker_engine.mouse_button = self.var_mouse_button.get().lower()
        self._clicker_engine.click_type = self.var_click_type.get().lower()

        if self.var_repeat_mode.get() == "repeat":
            try:
                count = int(self.var_repeat_count.get())
                self._clicker_engine.repeat_count = max(1, count)
            except ValueError:
                self._clicker_engine.repeat_count = 1
        else:
            self._clicker_engine.repeat_count = -1

        if self.var_position_mode.get() == "pick":
            try:
                x = int(self.var_pick_x.get())
                y = int(self.var_pick_y.get())
                self._clicker_engine.target_position = (x, y)
            except ValueError:
                messagebox.showerror("Fehler", "Ungültige Koordinaten!")
                return
        else:
            self._clicker_engine.target_position = None

        self._clicker_engine.start()
        self._update_ui_state(running=True)

    def _stop_clicking(self):
        self._clicker_engine.stop()
        self._update_ui_state(running=False)

    def _on_clicking_finished(self):
        self.root.after(0, lambda: self._update_ui_state(running=False))

    def _update_ui_state(self, running: bool):
        if running:
            self.var_status.set("Läuft...")
            self.label_status.configure(foreground=COLORS["success"])
            self.btn_start.config(state="disabled")
            self.btn_stop.config(state="normal")
            for widget in [
                self.entry_hours,
                self.entry_minutes,
                self.entry_seconds,
                self.entry_milliseconds,
                self.radio_repeat,
                self.radio_until_stopped,
                self.spinbox_repeat,
                self.radio_current,
                self.radio_pick,
                self.btn_pick_location,
            ]:
                try:
                    widget.config(state="disabled")
                except tk.TclError:
                    pass
        else:
            self.var_status.set("Bereit")
            self.label_status.configure(foreground=COLORS["text"])
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            for widget in [
                self.entry_hours,
                self.entry_minutes,
                self.entry_seconds,
                self.entry_milliseconds,
            ]:
                widget.config(state="normal")
            self._on_repeat_mode_changed()
            self._on_position_mode_changed()

    def _validate_inputs(self) -> bool:
        try:
            hours = validate_interval_component(self.var_hours.get(), "hours")
            minutes = validate_interval_component(self.var_minutes.get(), "minutes")
            seconds = validate_interval_component(self.var_seconds.get(), "seconds")
            milliseconds = validate_interval_component(self.var_milliseconds.get(), "milliseconds")

            total_ms = (hours * 3600000) + (minutes * 60000) + (seconds * 1000) + milliseconds
            if total_ms < 1:
                messagebox.showerror("Fehler", "Das Intervall muss mindestens 1 Millisekunde betragen!")
                return False

            if self.var_position_mode.get() == "pick":
                try:
                    int(self.var_pick_x.get())
                    int(self.var_pick_y.get())
                except ValueError:
                    messagebox.showerror("Fehler", "Ungültige Koordinaten!")
                    return False

            return True
        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültige Eingabe: {e}")
            return False

    def _register_hotkeys(self):
        def start_clicking():
            if not self._clicker_engine.is_running:
                self._start_clicking()

        def stop_clicking():
            if self._clicker_engine.is_running:
                self._stop_clicking()

        self._hotkey_manager.set_start_hotkey("f6", None, start_clicking)
        self._hotkey_manager.set_stop_hotkey("f7", None, stop_clicking)
        self._update_hotkey_labels()

    def _update_hotkey_labels(self):
        start_key = self._hotkey_manager.get_start_hotkey_string().upper()
        stop_key = self._hotkey_manager.get_stop_hotkey_string().upper()
        self.var_start_summary.set(start_key)
        self.var_stop_summary.set(stop_key)
        self.btn_start.config(text=f"Start ({start_key})")
        self.btn_stop.config(text=f"Stopp ({stop_key})")

    def _open_hotkey_dialog(self):
        def on_save(start_key: str, stop_key: str, modifiers: Optional[list]):
            def start_clicking():
                if not self._clicker_engine.is_running:
                    self._start_clicking()

            def stop_clicking():
                if self._clicker_engine.is_running:
                    self._stop_clicking()

            self._hotkey_manager.unregister_all()
            self._hotkey_manager.set_start_hotkey(start_key, modifiers, start_clicking)
            self._hotkey_manager.set_stop_hotkey(stop_key, modifiers, stop_clicking)
            self._update_hotkey_labels()

            if self._settings:
                self._settings.start_hotkey = start_key
                self._settings.stop_hotkey = stop_key
                self._settings.hotkey_modifiers = modifiers if modifiers else []
                self._settings_manager.save_settings(self._settings)

        HotkeyDialog(self.root, self._hotkey_manager, on_save)

    def _open_record_window(self):
        RecordWindow(self.root, self._recorder_service)

    def _load_settings(self):
        self._settings = self._settings_manager.load_settings()

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
        if not self._settings:
            self._settings = AppSettings()

        try:
            self._settings.default_hours = validate_interval_component(self.var_hours.get(), "hours")
            self._settings.default_minutes = validate_interval_component(self.var_minutes.get(), "minutes")
            self._settings.default_seconds = validate_interval_component(self.var_seconds.get(), "seconds")
            self._settings.default_milliseconds = validate_interval_component(
                self.var_milliseconds.get(), "milliseconds"
            )
            self._settings.default_mouse_button = self.var_mouse_button.get().lower()
            self._settings.default_click_type = self.var_click_type.get().lower()
            self._settings.default_repeat_count = int(self.var_repeat_count.get())
            self._settings.default_repeat_until_stopped = self.var_repeat_mode.get() == "until_stopped"
            self._settings.default_use_current_location = self.var_position_mode.get() == "current"
            self._settings.default_pick_x = int(self.var_pick_x.get())
            self._settings.default_pick_y = int(self.var_pick_y.get())
            self._settings_manager.save_settings(self._settings)
        except Exception as e:
            print(f"Fehler beim Speichern der Settings: {e}")

    def on_closing(self):
        try:
            if self._clicker_engine.is_running:
                self._clicker_engine.stop()
            try:
                self._hotkey_manager.unregister_all()
            except Exception:
                pass
            try:
                self._save_settings()
            except Exception:
                pass
            self.root.quit()
            self.root.destroy()
        except Exception:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass

"""RecordWindow - GUI für Record & Playback Funktionalität."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

from src.services.recorder import RecorderService
from src.models.click_event import ClickEvent
from src.gui.theme import apply_theme


class RecordWindow:
    """Fenster für Record & Playback Funktionalität."""

    def __init__(self, parent: tk.Tk, recorder_service: RecorderService):
        self.parent = parent
        self._recorder_service = recorder_service

        self.window = tk.Toplevel(parent)
        self.window.title("Aufnahme & Wiedergabe")
        self.window.geometry("680x520")
        self.window.minsize(620, 460)
        self.window.resizable(True, True)
        self.window.transient(parent)
        apply_theme(self.window)

        self.var_event_count = tk.StringVar(value="0 Ereignisse")
        self.var_status = tk.StringVar(value="Bereit")

        self._create_widgets()
        self._setup_callbacks()
        self._center_window()

    def _create_widgets(self):
        container = ttk.Frame(self.window, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container, style="Surface.TFrame", padding=(14, 12))
        header.pack(fill=tk.X, pady=(0, 12))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Aufnahme & Wiedergabe", style="HeaderTitle.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(header, textvariable=self.var_status, style="HeaderSubtitle.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=(2, 0)
        )
        ttk.Label(header, textvariable=self.var_event_count, style="Kpi.TLabel").grid(
            row=0, column=1, rowspan=2, sticky=tk.E
        )

        list_frame = ttk.LabelFrame(container, text=" Aufgezeichnete Klicks ", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("#", "Position", "Button", "Type", "Delay")
        self.tree_events = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.tree_events.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_events.heading("#", text="#")
        self.tree_events.heading("Position", text="Position")
        self.tree_events.heading("Button", text="Taste")
        self.tree_events.heading("Type", text="Typ")
        self.tree_events.heading("Delay", text="Pause (s)")

        self.tree_events.column("#", width=40, anchor=tk.CENTER)
        self.tree_events.column("Position", width=130)
        self.tree_events.column("Button", width=80)
        self.tree_events.column("Type", width=80)
        self.tree_events.column("Delay", width=90, anchor=tk.E)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_events.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_events.configure(yscrollcommand=scrollbar.set)

        btn_container = ttk.Frame(container)
        btn_container.pack(fill=tk.X)
        btn_container.columnconfigure(0, weight=1)
        btn_container.columnconfigure(1, weight=1)
        btn_container.columnconfigure(2, weight=1)

        record_frame = ttk.LabelFrame(btn_container, text=" Aufnahme ", padding=10)
        record_frame.grid(row=0, column=0, sticky=tk.EW, padx=(0, 6))
        record_frame.columnconfigure(0, weight=1)
        record_frame.columnconfigure(1, weight=1)
        self.btn_start_record = ttk.Button(
            record_frame, text="Aufnahme starten", command=self._start_recording, style="Accent.TButton"
        )
        self.btn_start_record.grid(row=0, column=0, sticky=tk.EW, padx=(0, 4))
        self.btn_stop_record = ttk.Button(
            record_frame, text="Aufnahme stoppen", command=self._stop_recording, state="disabled"
        )
        self.btn_stop_record.grid(row=0, column=1, sticky=tk.EW, padx=(4, 0))

        playback_frame = ttk.LabelFrame(btn_container, text=" Wiedergabe ", padding=10)
        playback_frame.grid(row=0, column=1, sticky=tk.EW, padx=6)
        playback_frame.columnconfigure(0, weight=1)
        playback_frame.columnconfigure(1, weight=1)
        self.btn_play = ttk.Button(
            playback_frame, text="Abspielen", command=self._play_sequence, style="Success.TButton"
        )
        self.btn_play.grid(row=0, column=0, sticky=tk.EW, padx=(0, 4))
        self.btn_stop_play = ttk.Button(playback_frame, text="Stopp", command=self._stop_playback, state="disabled")
        self.btn_stop_play.grid(row=0, column=1, sticky=tk.EW, padx=(4, 0))

        file_frame = ttk.LabelFrame(btn_container, text=" Datei ", padding=10)
        file_frame.grid(row=0, column=2, sticky=tk.EW, padx=(6, 0))
        file_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(2, weight=1)
        ttk.Button(file_frame, text="Speichern", command=self._save_sequence).grid(
            row=0, column=0, sticky=tk.EW, padx=(0, 4)
        )
        ttk.Button(file_frame, text="Laden", command=self._load_sequence).grid(row=0, column=1, sticky=tk.EW, padx=4)
        ttk.Button(file_frame, text="Leeren", command=self._clear_events).grid(
            row=0, column=2, sticky=tk.EW, padx=(4, 0)
        )

    def _setup_callbacks(self):
        def on_record(count: int):
            self.window.after(0, lambda: self._on_event_recorded(count))

        def on_playback(current: int, total: int):
            self.window.after(0, lambda: self._on_playback_progress(current, total))

        def on_finished():
            self.window.after(0, self._on_playback_finished)

        self._recorder_service.set_on_record_callback(on_record)
        self._recorder_service.set_on_playback_callback(on_playback)
        self._recorder_service.set_on_finished_callback(on_finished)

    def _start_recording(self):
        self._recorder_service.start_recording()
        self.var_status.set("Aufnahme läuft...")
        self.btn_start_record.config(state="disabled")
        self.btn_stop_record.config(state="normal")

    def _stop_recording(self):
        events = self._recorder_service.stop_recording()
        self.var_status.set(f"Aufnahme beendet ({len(events)} Ereignisse)")
        self.btn_start_record.config(state="normal")
        self.btn_stop_record.config(state="disabled")
        self._update_event_list()

    def _play_sequence(self):
        events = self._recorder_service.recorded_events
        if not events:
            messagebox.showwarning("Hinweis", "Keine Ereignisse zum Abspielen vorhanden!")
            return

        self._recorder_service.playback(events, repeat=False)
        self.var_status.set("Wiedergabe läuft...")
        self.btn_play.config(state="disabled")
        self.btn_stop_play.config(state="normal")

    def _stop_playback(self):
        self._recorder_service.stop_playback()
        self.var_status.set("Wiedergabe gestoppt")
        self.btn_play.config(state="normal")
        self.btn_stop_play.config(state="disabled")

    def _on_event_recorded(self, count: int):
        self.var_event_count.set(f"{count} Ereignisse")
        self._update_event_list()

    def _on_playback_progress(self, current: int, total: int):
        self.var_status.set(f"Wiedergabe {current}/{total}")

    def _on_playback_finished(self):
        self.var_status.set("Wiedergabe beendet")
        self.btn_play.config(state="normal")
        self.btn_stop_play.config(state="disabled")

    def _update_event_list(self):
        for item in self.tree_events.get_children():
            self.tree_events.delete(item)

        events = self._recorder_service.recorded_events
        for i, event in enumerate(events, 1):
            self.tree_events.insert(
                "",
                tk.END,
                values=(
                    i,
                    f"({event.position[0]}, {event.position[1]})",
                    event.button.capitalize(),
                    event.click_type.capitalize(),
                    f"{event.delay_from_previous:.3f}",
                ),
            )

        self.var_event_count.set(f"{len(events)} Ereignisse")

    def _save_sequence(self):
        events = self._recorder_service.recorded_events
        if not events:
            messagebox.showwarning("Hinweis", "Keine Ereignisse zum Speichern vorhanden!")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")],
        )

        if filename:
            try:
                data = [event.to_dict() for event in events]
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Erfolg", f"Sequenz gespeichert:\n{filename}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def _load_sequence(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")]
        )

        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    data = json.load(f)

                events = [ClickEvent.from_dict(item) for item in data]
                self._recorder_service.load_events(events)
                self._update_event_list()
                self.var_status.set(f"{len(events)} Ereignisse geladen")
                messagebox.showinfo("Erfolg", f"{len(events)} Ereignisse geladen.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden: {e}")

    def _clear_events(self):
        if messagebox.askyesno("Bestätigung", "Alle Ereignisse wirklich löschen?"):
            self._recorder_service.clear_events()
            self._update_event_list()
            self.var_status.set("Liste geleert")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

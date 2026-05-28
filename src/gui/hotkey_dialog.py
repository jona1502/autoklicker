"""HotkeyDialog - Dialog zum Konfigurieren der Hotkeys."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from src.core.hotkey_manager import HotkeyManager
from src.gui.theme import apply_theme


class HotkeyDialog:
    """Dialog zum Konfigurieren der Hotkeys."""

    def __init__(
        self,
        parent: tk.Tk,
        hotkey_manager: HotkeyManager,
        on_save: Optional[Callable[[str, str, Optional[list]], None]] = None,
    ):
        self.parent = parent
        self._hotkey_manager = hotkey_manager
        self._on_save = on_save

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Hotkey-Einstellungen")
        self.dialog.geometry("460x360")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        apply_theme(self.dialog)

        self.var_start_key = tk.StringVar(value="f6")
        self.var_stop_key = tk.StringVar(value="f7")
        self.var_ctrl = tk.BooleanVar(value=False)
        self.var_alt = tk.BooleanVar(value=False)
        self.var_shift = tk.BooleanVar(value=False)

        self._create_widgets()
        self._center_dialog()

    def _create_widgets(self):
        container = ttk.Frame(self.dialog, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container, style="Surface.TFrame", padding=(12, 10))
        header.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(header, text="Globale Tastenkürzel", style="HeaderTitle.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Start und Stopp sollten unterschiedliche Tasten sein.",
            style="HeaderSubtitle.TLabel",
        ).pack(anchor=tk.W, pady=(2, 0))

        start_frame = ttk.LabelFrame(container, text=" Start ", padding=12)
        start_frame.pack(fill=tk.X, pady=4)
        start_frame.columnconfigure(1, weight=1)
        ttk.Label(start_frame, text="Taste", style="Muted.TLabel").grid(row=0, column=0, sticky=tk.W, padx=4)
        ttk.Entry(start_frame, textvariable=self.var_start_key, width=18).grid(row=0, column=1, padx=8, sticky=tk.EW)
        ttk.Label(start_frame, text="z.B. f6, space", style="Muted.TLabel").grid(row=0, column=2, sticky=tk.W)

        stop_frame = ttk.LabelFrame(container, text=" Stopp ", padding=12)
        stop_frame.pack(fill=tk.X, pady=4)
        stop_frame.columnconfigure(1, weight=1)
        ttk.Label(stop_frame, text="Taste", style="Muted.TLabel").grid(row=0, column=0, sticky=tk.W, padx=4)
        ttk.Entry(stop_frame, textvariable=self.var_stop_key, width=18).grid(row=0, column=1, padx=8, sticky=tk.EW)
        ttk.Label(stop_frame, text="z.B. f7, escape", style="Muted.TLabel").grid(row=0, column=2, sticky=tk.W)

        modifier_frame = ttk.LabelFrame(container, text=" Modifier (optional) ", padding=12)
        modifier_frame.pack(fill=tk.X, pady=8)
        ttk.Checkbutton(modifier_frame, text="Strg", variable=self.var_ctrl).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(modifier_frame, text="Alt", variable=self.var_alt).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(modifier_frame, text="Umschalt", variable=self.var_shift).pack(side=tk.LEFT, padx=8)

        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(button_frame, text="Abbrechen", command=self._on_cancel).pack(side=tk.RIGHT, padx=4)
        ttk.Button(button_frame, text="Speichern", command=self._on_ok, style="Accent.TButton").pack(
            side=tk.RIGHT, padx=4
        )

    def _center_dialog(self):
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def _on_ok(self):
        start_key = self.var_start_key.get().strip().lower()
        stop_key = self.var_stop_key.get().strip().lower()

        if not start_key or not stop_key:
            messagebox.showerror("Fehler", "Bitte gültige Hotkeys eingeben!")
            return

        if start_key == stop_key:
            messagebox.showerror("Fehler", "Start- und Stopp-Taste müssen unterschiedlich sein!")
            return

        modifiers = []
        if self.var_ctrl.get():
            modifiers.append("ctrl")
        if self.var_alt.get():
            modifiers.append("alt")
        if self.var_shift.get():
            modifiers.append("shift")

        if self._on_save:
            try:
                self._on_save(start_key, stop_key, modifiers if modifiers else None)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
                return

        self.dialog.destroy()

    def _on_cancel(self):
        self.dialog.destroy()

"""HotkeyDialog - Dialog zum Konfigurieren der Hotkeys."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from src.core.hotkey_manager import HotkeyManager


class HotkeyDialog:
    """Dialog zum Konfigurieren der Hotkeys."""

    def __init__(self, parent: tk.Tk, hotkey_manager: HotkeyManager, 
                 on_save: Optional[Callable[[str, str, Optional[list]], None]] = None):
        """
        Initialisiert den Hotkey-Dialog.

        Args:
            parent: Parent-Window
            hotkey_manager: HotkeyManager Instanz
            on_save: Callback der aufgerufen wird wenn gespeichert wird
        """
        self.parent = parent
        self._hotkey_manager = hotkey_manager
        self._on_save = on_save
        self._result = None

        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Hotkey Settings")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Variablen
        self.var_start_key = tk.StringVar(value="f6")
        self.var_stop_key = tk.StringVar(value="f6")
        self.var_ctrl = tk.BooleanVar(value=False)
        self.var_alt = tk.BooleanVar(value=False)
        self.var_shift = tk.BooleanVar(value=False)

        # UI erstellen
        self._create_widgets()

        # Zentrieren
        self._center_dialog()

    def _create_widgets(self):
        """Erstellt die UI-Widgets."""
        # Start Hotkey
        start_frame = ttk.LabelFrame(self.dialog, text="Start Hotkey", padding=10)
        start_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(start_frame, text="Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        entry_start = ttk.Entry(start_frame, textvariable=self.var_start_key, width=15)
        entry_start.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(start_frame, text="(z.B. f6, space, enter)").grid(row=0, column=2, sticky=tk.W, padx=5)

        # Stop Hotkey
        stop_frame = ttk.LabelFrame(self.dialog, text="Stop Hotkey", padding=10)
        stop_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(stop_frame, text="Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        entry_stop = ttk.Entry(stop_frame, textvariable=self.var_stop_key, width=15)
        entry_stop.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(stop_frame, text="(z.B. f6, space, enter)").grid(row=0, column=2, sticky=tk.W, padx=5)

        # Modifier Keys
        modifier_frame = ttk.LabelFrame(self.dialog, text="Modifier Keys (optional)", padding=10)
        modifier_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Checkbutton(modifier_frame, text="Ctrl", variable=self.var_ctrl).grid(row=0, column=0, padx=5, pady=5)
        ttk.Checkbutton(modifier_frame, text="Alt", variable=self.var_alt).grid(row=0, column=1, padx=5, pady=5)
        ttk.Checkbutton(modifier_frame, text="Shift", variable=self.var_shift).grid(row=0, column=2, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.RIGHT, padx=5)

    def _center_dialog(self):
        """Zentriert den Dialog über dem Parent-Fenster."""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def _on_ok(self):
        """Wird aufgerufen wenn OK geklickt wird."""
        start_key = self.var_start_key.get().strip().lower()
        stop_key = self.var_stop_key.get().strip().lower()

        if not start_key or not stop_key:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige Hotkeys ein!")
            return

        # Modifier-Keys sammeln
        modifiers = []
        if self.var_ctrl.get():
            modifiers.append("ctrl")
        if self.var_alt.get():
            modifiers.append("alt")
        if self.var_shift.get():
            modifiers.append("shift")

        # Callback aufrufen
        if self._on_save:
            try:
                self._on_save(start_key, stop_key, modifiers if modifiers else None)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
                return

        self.dialog.destroy()

    def _on_cancel(self):
        """Wird aufgerufen wenn Cancel geklickt wird."""
        self.dialog.destroy()


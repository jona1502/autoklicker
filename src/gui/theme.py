"""Gemeinsames UI-Theme für alle AutoKlicker-Fenster."""
import tkinter as tk
from tkinter import ttk

APP_VERSION = "1.1.0"
APP_NAME = "AutoKlicker"

COLORS = {
    "bg": "#111315",
    "surface": "#1b1f22",
    "surface_light": "#252b2f",
    "surface_hover": "#30383d",
    "text": "#edf2f4",
    "text_muted": "#9aa6ad",
    "accent": "#4fb3bf",
    "accent_hover": "#66c7d1",
    "success": "#87c96b",
    "danger": "#f06d62",
    "warning": "#f2b84b",
    "border": "#3b454b",
    "input": "#15191c",
}


def apply_theme(root: tk.Tk) -> ttk.Style:
    """Wendet das dunkle Theme auf Root und ttk-Widgets an."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(bg=COLORS["bg"])

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Surface.TFrame", background=COLORS["surface"])
    style.configure("Toolbar.TFrame", background=COLORS["surface_light"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("Surface.TLabel", background=COLORS["surface"], foreground=COLORS["text"])
    style.configure("Toolbar.TLabel", background=COLORS["surface_light"], foreground=COLORS["text"])
    style.configure("Muted.TLabel", foreground=COLORS["text_muted"])
    style.configure("SurfaceMuted.TLabel", background=COLORS["surface"], foreground=COLORS["text_muted"])
    style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground=COLORS["text"])
    style.configure("HeaderTitle.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=("Segoe UI", 20, "bold"))
    style.configure("HeaderSubtitle.TLabel", background=COLORS["surface"], foreground=COLORS["text_muted"], font=("Segoe UI", 9))
    style.configure("SectionTitle.TLabel", font=("Segoe UI", 10, "bold"), foreground=COLORS["text"])
    style.configure("Subtitle.TLabel", font=("Segoe UI", 9), foreground=COLORS["text_muted"])
    style.configure("Warning.TLabel", foreground=COLORS["warning"], font=("Segoe UI", 10, "bold"))
    style.configure("Status.TLabel", foreground=COLORS["text_muted"], font=("Segoe UI", 9))
    style.configure("Hotkey.TLabel", foreground=COLORS["warning"], font=("Segoe UI", 10, "bold"))
    style.configure("Kpi.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=("Segoe UI", 15, "bold"))

    style.configure(
        "TLabelframe",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "TEntry",
        fieldbackground=COLORS["input"],
        foreground=COLORS["text"],
        insertcolor=COLORS["text"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        padding=(7, 5),
    )
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["input"],
        foreground=COLORS["text"],
        background=COLORS["input"],
        arrowcolor=COLORS["text"],
        bordercolor=COLORS["border"],
        padding=(7, 5),
    )
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["input"])])

    style.configure(
        "TSpinbox",
        fieldbackground=COLORS["input"],
        foreground=COLORS["text"],
        background=COLORS["input"],
        arrowcolor=COLORS["text"],
        bordercolor=COLORS["border"],
        padding=(7, 5),
    )

    style.configure(
        "TRadiobutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.map("TRadiobutton", background=[("active", COLORS["surface"])])

    style.configure(
        "TCheckbutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )
    style.map("TCheckbutton", background=[("active", COLORS["surface"])])

    style.configure(
        "TButton",
        background=COLORS["surface_light"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        focusthickness=0,
        padding=(13, 7),
    )
    style.map(
        "TButton",
        background=[("active", COLORS["surface_hover"]), ("disabled", COLORS["surface"])],
        foreground=[("disabled", COLORS["text_muted"])],
    )

    style.configure(
        "Accent.TButton",
        background=COLORS["accent"],
        foreground="#081013",
        font=("Segoe UI", 10, "bold"),
    )
    style.map("Accent.TButton", background=[("active", COLORS["accent_hover"]), ("disabled", COLORS["surface"])])

    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground="#081013",
        font=("Segoe UI", 10, "bold"),
    )
    style.map("Success.TButton", background=[("active", "#9bdc7c"), ("disabled", COLORS["surface"])])

    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground="#081013",
        font=("Segoe UI", 10, "bold"),
    )
    style.map("Danger.TButton", background=[("active", "#ff8076"), ("disabled", COLORS["surface"])])

    style.configure(
        "Treeview",
        background=COLORS["input"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["input"],
        bordercolor=COLORS["border"],
        rowheight=28,
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("Segoe UI", 9, "bold"),
    )
    style.map("Treeview", background=[("selected", COLORS["accent"])], foreground=[("selected", "#081013")])

    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["surface"],
        troughcolor=COLORS["bg"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["text"],
    )

    return style


def configure_tk_widget(widget: tk.Widget, **kwargs) -> None:
    """Setzt Standard-Hintergrund für klassische tk-Widgets."""
    defaults = {"bg": COLORS["bg"], "fg": COLORS["text"]}
    defaults.update(kwargs)
    try:
        widget.configure(**{k: v for k, v in defaults.items() if k in widget.keys() or k in ("bg", "fg")})
    except tk.TclError:
        pass

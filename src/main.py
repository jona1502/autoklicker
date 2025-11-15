"""Main Entry Point der AutoKlicker-Anwendung."""
import tkinter as tk
import sys
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow


def main():
    """Hauptfunktion der Anwendung."""
    # Root-Window erstellen
    root = tk.Tk()
    
    # MainWindow erstellen
    app = MainWindow(root)
    
    # Window-Close-Handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Main-Loop starten
    root.mainloop()


if __name__ == "__main__":
    main()


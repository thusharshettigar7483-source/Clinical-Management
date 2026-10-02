"""
Medicare Specialist Portal — Application Entry Point.
A modern desktop hospital and specialist clinic management system.
"""

import sys
import os
import ctypes

# Add project root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.main_window import MainWindow

def setup_windows_dpi_awareness():
    """Sets Per-Monitor DPI awareness on Windows for ultra-crisp fonts."""
    if sys.platform.startswith("win"):
        try:
            # Set DPI Awareness to Per-Monitor High DPI Aware
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

def main():
    """Initializes and runs the Medicare Specialist Portal desktop application."""
    setup_windows_dpi_awareness()
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
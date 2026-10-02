"""
Pill status badge component for Medicare Specialist Portal.
Displays clean color-coded badges for 'Pending', 'Confirmed', and 'Rejected'.
"""

import customtkinter as ctk
from app.config import STATUS_COLORS, STATUS_PENDING, STATUS_CONFIRMED, STATUS_REJECTED

class StatusBadge(ctk.CTkFrame):
    """
    Renders a modern rounded pill badge for appointment statuses.
    """
    def __init__(self, master, status: str = STATUS_PENDING, **kwargs):
        super().__init__(
            master,
            corner_radius=12,
            border_width=1,
            height=26,
            **kwargs
        )
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self,
            text=status,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="center"
        )
        self.label.grid(row=0, column=0, padx=10, pady=2)

        self.set_status(status)

    def set_status(self, status: str) -> None:
        """Update badge appearance based on status."""
        cfg = STATUS_COLORS.get(status, STATUS_COLORS[STATUS_PENDING])
        
        self.configure(
            fg_color=(cfg["bg"], cfg["dark_bg"]),
            border_color=(cfg["border"], cfg["dark_border"])
        )
        self.label.configure(
            text=f"● {status}",
            text_color=(cfg["text"], cfg["dark_text"])
        )

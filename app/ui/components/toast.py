"""
Modern Floating Toast Notification for CustomTkinter.
Supports Success, Error, Warning, and Info types with smooth auto-dismiss.
"""

import customtkinter as ctk
from typing import Optional, Literal
from app.config import COLORS

ToastType = Literal["success", "error", "warning", "info"]

class ToastNotification(ctk.CTkFrame):
    """
    Floating animated toast banner for non-intrusive feedback.
    """
    def __init__(self, master, text: str = "", toast_type: ToastType = "info", duration_ms: int = 3500):
        super().__init__(
            master,
            corner_radius=12,
            border_width=1,
            fg_color="#FFFFFF",
            border_color="#CBD5E1"
        )
        self.master = master
        self.duration_ms = duration_ms
        self._timer_id = None
        self._is_showing = False

        # Configure colors by type
        self._type_configs = {
            "success": {
                "fg_light": "#ECFDF5",
                "fg_dark": "#064E3B",
                "border_light": "#A7F3D0",
                "border_dark": "#047857",
                "text_light": "#065F46",
                "text_dark": "#6EE7B7",
                "icon": "✓",
                "badge_bg": "#10B981"
            },
            "error": {
                "fg_light": "#FEF2F2",
                "fg_dark": "#7F1D1D",
                "border_light": "#FECACA",
                "border_dark": "#DC2626",
                "text_light": "#991B1B",
                "text_dark": "#FCA5A5",
                "icon": "✕",
                "badge_bg": "#EF4444"
            },
            "warning": {
                "fg_light": "#FFFBEB",
                "fg_dark": "#78350F",
                "border_light": "#FDE68A",
                "border_dark": "#D97706",
                "text_light": "#92400E",
                "text_dark": "#FDE68A",
                "icon": "⚠",
                "badge_bg": "#F59E0B"
            },
            "info": {
                "fg_light": "#EFF6FF",
                "fg_dark": "#1E3A8A",
                "border_light": "#BFDBFE",
                "border_dark": "#2563EB",
                "text_light": "#1E40AF",
                "text_dark": "#93C5FD",
                "icon": "ℹ",
                "badge_bg": "#3B82F6"
            }
        }

        # Layout container
        self.grid_columnconfigure(1, weight=1)

        # Icon badge
        self.icon_label = ctk.CTkLabel(
            self,
            text="✓",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF",
            fg_color="#10B981",
            corner_radius=10,
            width=24,
            height=24
        )
        self.icon_label.grid(row=0, column=0, padx=(12, 8), pady=10)

        # Message Label
        self.msg_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=13, weight="normal"),
            anchor="w",
            justify="left",
            wraplength=450
        )
        self.msg_label.grid(row=0, column=1, padx=(0, 12), pady=10, sticky="w")

        # Close button
        self.close_btn = ctk.CTkButton(
            self,
            text="×",
            width=20,
            height=20,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent",
            hover_color=("#E2E8F0", "#334155"),
            text_color=("#64748B", "#94A3B8"),
            command=self.dismiss
        )
        self.close_btn.grid(row=0, column=2, padx=(0, 10), pady=10)

        if text:
            self.show(text, toast_type, duration_ms)

    def show(self, text: str, toast_type: ToastType = "info", duration_ms: Optional[int] = None) -> None:
        """Displays or updates the toast notification."""
        if duration_ms is not None:
            self.duration_ms = duration_ms

        cfg = self._type_configs.get(toast_type, self._type_configs["info"])
        
        # Apply theme colors
        self.configure(
            fg_color=(cfg["fg_light"], cfg["fg_dark"]),
            border_color=(cfg["border_light"], cfg["border_dark"])
        )
        self.icon_label.configure(
            text=cfg["icon"],
            fg_color=cfg["badge_bg"]
        )
        self.msg_label.configure(
            text=text,
            text_color=(cfg["text_light"], cfg["text_dark"])
        )

        # Cancel any previous timer
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        # Position at top center
        self.place(relx=0.5, rely=0.06, anchor="center")
        self.lift()
        self._is_showing = True

        # Schedule auto-dismiss
        if self.duration_ms > 0:
            self._timer_id = self.after(self.duration_ms, self.dismiss)

    def dismiss(self) -> None:
        """Hides the toast."""
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        if self._is_showing:
            self.place_forget()
            self._is_showing = False

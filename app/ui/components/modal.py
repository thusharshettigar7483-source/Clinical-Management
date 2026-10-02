"""
Modern Modal Dialogs for CustomTkinter.
Provides custom confirmation, alert, and prompt dialogs.
"""

import customtkinter as ctk
from typing import Callable, Optional
from app.config import COLORS

class ConfirmationModal(ctk.CTkToplevel):
    """
    Modern modal confirmation dialog centered on parent window.
    """
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        confirm_type: str = "primary",  # "primary" | "danger" | "accent"
        on_confirm: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.parent = parent
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Set size and center on parent
        width = 420
        height = 220
        self.geometry(f"{width}x{height}")

        # Position modal relative to parent window
        parent.update_idletasks()
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
            self.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        self._build_ui(title, message, confirm_text, cancel_text, confirm_type)

    def _build_ui(self, title: str, message: str, confirm_text: str, cancel_text: str, confirm_type: str) -> None:
        container = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Title Label
        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=16, pady=(16, 6))

        # Message Label
        msg_label = ctk.CTkLabel(
            container,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color=("#475569", "#94A3B8"),
            anchor="w",
            justify="left",
            wraplength=350
        )
        msg_label.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Buttons Row
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 16), side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            width=100,
            height=36,
            corner_radius=8,
            fg_color=("#F1F5F9", "#334155"),
            hover_color=("#E2E8F0", "#475569"),
            text_color=("#334155", "#E2E8F0"),
            command=self._handle_cancel
        )
        cancel_btn.pack(side="right", padx=(8, 0))

        if confirm_type == "danger":
            btn_fg = COLORS["danger"]
            btn_hover = COLORS["danger_hover"]
        elif confirm_type == "accent":
            btn_fg = COLORS["accent"]
            btn_hover = COLORS["accent_hover"]
        else:
            btn_fg = COLORS["primary"]
            btn_hover = COLORS["primary_hover"]

        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            width=110,
            height=36,
            corner_radius=8,
            fg_color=btn_fg,
            hover_color=btn_hover,
            text_color="#FFFFFF",
            command=self._handle_confirm
        )
        confirm_btn.pack(side="right")

    def _handle_confirm(self) -> None:
        self.destroy()
        if self.on_confirm:
            self.on_confirm()

    def _handle_cancel(self) -> None:
        self.destroy()
        if self.on_cancel:
            self.on_cancel()

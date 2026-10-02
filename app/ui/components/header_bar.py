"""
Header Bar Component for Medicare Specialist Portal.
Provides brand branding, active user info, role badge, theme switcher, and logout CTA.
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from app.config import APP_NAME, COLORS

class HeaderBar(ctk.CTkFrame):
    """
    Top application navigation bar with branding, user info, theme toggle, and logout.
    """
    def __init__(
        self,
        master,
        user_info: Optional[Dict[str, Any]] = None,
        on_logout: Optional[Callable[[], None]] = None,
        on_theme_toggle: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            height=68,
            corner_radius=0,
            fg_color=("#FFFFFF", "#1C2541"),
            border_width=1,
            border_color=("#E2E8F0", "#3A506B"),
            **kwargs
        )
        self.user_info = user_info or {}
        self.on_logout = on_logout
        self.on_theme_toggle = on_theme_toggle

        self.pack_propagate(False)
        self._build_ui()

    def _build_ui(self) -> None:
        # Left branding
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(side="left", padx=24, pady=10)

        logo_badge = ctk.CTkLabel(
            brand_frame,
            text="🏥",
            font=ctk.CTkFont(size=22),
            width=36,
            height=36,
            corner_radius=10,
            fg_color=("#E0F2FE", "#0C4A6E")
        )
        logo_badge.pack(side="left", padx=(0, 12))

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side="left")

        brand_title = ctk.CTkLabel(
            title_box,
            text=APP_NAME,
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        brand_title.pack(anchor="w")

        brand_sub = ctk.CTkLabel(
            title_box,
            text="Clinical Management & Specialist Network",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8")
        )
        brand_sub.pack(anchor="w")

        # Right side actions
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", padx=24, pady=10)

        # Logout Button
        logout_btn = ctk.CTkButton(
            right_frame,
            text="🚪 Logout",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=90,
            height=34,
            corner_radius=8,
            fg_color=("#FEE2E2", "#7F1D1D"),
            hover_color=("#FECACA", "#991B1B"),
            text_color=("#B91C1C", "#FCA5A5"),
            command=self._handle_logout
        )
        logout_btn.pack(side="right", padx=(12, 0))

        # Theme toggle switch
        self.theme_switch = ctk.CTkSwitch(
            right_frame,
            text="🌙 Dark",
            font=ctk.CTkFont(size=12),
            text_color=("#475569", "#CBD5E1"),
            command=self._handle_theme_toggle,
            width=40
        )
        # Check current appearance mode
        current_mode = ctk.get_appearance_mode().lower()
        if current_mode == "dark":
            self.theme_switch.select()
            self.theme_switch.configure(text="🌙 Dark")
        else:
            self.theme_switch.deselect()
            self.theme_switch.configure(text="☀️ Light")
        self.theme_switch.pack(side="right", padx=(16, 8))

        # User Info & Role Badge
        if self.user_info:
            uname = self.user_info.get("username", "Guest")
            role = self.user_info.get("role", "patient").capitalize()

            user_container = ctk.CTkFrame(right_frame, fg_color="transparent")
            user_container.pack(side="right", padx=(0, 12))

            welcome_lbl = ctk.CTkLabel(
                user_container,
                text=f"Welcome, {uname}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#0F172A", "#F8FAFC")
            )
            welcome_lbl.pack(anchor="e")

            # Role pill
            role_fg = ("#D1FAE5", "#064E3B") if role == "Admin" else ("#E0F2FE", "#0C4A6E")
            role_text_color = ("#047857", "#6EE7B7") if role == "Admin" else ("#0369A1", "#7DD3FC")
            role_border = ("#A7F3D0", "#047857") if role == "Admin" else ("#BAE6FD", "#0369A1")

            role_pill = ctk.CTkFrame(
                user_container,
                corner_radius=10,
                border_width=1,
                fg_color=role_fg,
                border_color=role_border,
                height=18
            )
            role_pill.pack(anchor="e", pady=(2, 0))

            role_lbl = ctk.CTkLabel(
                role_pill,
                text=f"✦ {role.upper()}",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=role_text_color
            )
            role_lbl.pack(padx=6, pady=1)

    def _handle_theme_toggle(self) -> None:
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
            self.theme_switch.configure(text="🌙 Dark")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_switch.configure(text="☀️ Light")

        if self.on_theme_toggle:
            self.on_theme_toggle()

    def _handle_logout(self) -> None:
        if self.on_logout:
            self.on_logout()

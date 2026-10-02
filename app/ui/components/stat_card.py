"""
Metric Stat Card component for Admin Dashboard.
Displays high-level KPI counts with clean visual accents.
"""

import customtkinter as ctk
from app.config import COLORS

class StatCard(ctk.CTkFrame):
    """
    Card displaying a numeric metric with title, icon, and accent color.
    """
    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        icon: str = "📊",
        accent_color: str = "#0F4C81",
        subtitle: str = "",
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=14,
            border_width=1,
            fg_color=("#FFFFFF", "#1E293B"),
            border_color=("#E2E8F0", "#334155"),
            **kwargs
        )
        self.accent_color = accent_color

        self.grid_columnconfigure(0, weight=1)

        # Header with icon and title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(14, 4))

        # Select soft badge background based on accent color
        badge_bg_light = "#E0F2FE"
        badge_bg_dark = "#0C4A6E"
        if accent_color == COLORS["warning"]:
            badge_bg_light, badge_bg_dark = "#FEF3C7", "#451A03"
        elif accent_color == COLORS["accent"]:
            badge_bg_light, badge_bg_dark = "#D1FAE5", "#064E3B"
        elif accent_color == COLORS["danger"]:
            badge_bg_light, badge_bg_dark = "#FEE2E2", "#7F1D1D"
        elif accent_color == "#8B5CF6":
            badge_bg_light, badge_bg_dark = "#EDE9FE", "#4C1D95"

        self.icon_badge = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=ctk.CTkFont(size=14),
            width=30,
            height=30,
            corner_radius=8,
            fg_color=(badge_bg_light, badge_bg_dark),
            text_color=accent_color
        )
        self.icon_badge.pack(side="left", padx=(0, 10))

        self.title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        # Metric Value
        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        self.value_label.pack(fill="x", padx=16, pady=(2, 2))

        # Subtitle / trend indicator
        if subtitle:
            self.sub_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=("#94A3B8", "#64748B"),
                anchor="w"
            )
            self.sub_label.pack(fill="x", padx=16, pady=(0, 12))
        else:
            ctk.CTkFrame(self, height=8, fg_color="transparent").pack()

    def update_value(self, new_value: any) -> None:
        """Update displayed count/value."""
        self.value_label.configure(text=str(new_value))

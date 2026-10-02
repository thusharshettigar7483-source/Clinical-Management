"""
Modern Interactive Calendar & Date Picker Widget for CustomTkinter.
Restricts selection strictly to future dates (tomorrow onwards).
"""

import calendar
import datetime
from typing import Callable, Optional
import customtkinter as ctk
from app.config import COLORS

class CalendarDatePickerDialog(ctk.CTkToplevel):
    """
    Modern popup calendar for picking appointment dates.
    Enforces minimum selectable date of tomorrow.
    """
    def __init__(
        self,
        parent,
        current_date_str: Optional[str] = None,
        on_date_selected: Optional[Callable[[str], None]] = None
    ):
        super().__init__(parent)
        self.parent = parent
        self.on_date_selected = on_date_selected

        self.title("Select Appointment Date")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        width = 360
        height = 420
        self.geometry(f"{width}x{height}")

        # Center on parent
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

        self.today = datetime.date.today()
        self.min_date = self.today + datetime.timedelta(days=1)  # Tomorrow
        self.max_date = self.today + datetime.timedelta(days=90) # 90 days horizon

        # Parse current date or default to min_date (tomorrow)
        self.selected_date = self.min_date
        if current_date_str:
            try:
                parsed = datetime.datetime.strptime(current_date_str.strip(), "%Y-%m-%d").date()
                if parsed >= self.min_date:
                    self.selected_date = parsed
            except Exception:
                pass

        self.view_year = self.selected_date.year
        self.view_month = self.selected_date.month

        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # Header with Month/Year and navigation arrows
        nav_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12, pady=(12, 8))

        prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=("#F1F5F9", "#334155"),
            hover_color=("#E2E8F0", "#475569"),
            text_color=("#334155", "#E2E8F0"),
            command=self._prev_month
        )
        prev_btn.pack(side="left")

        self.month_year_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.month_year_label.pack(side="left", expand=True)

        next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=("#F1F5F9", "#334155"),
            hover_color=("#E2E8F0", "#475569"),
            text_color=("#334155", "#E2E8F0"),
            command=self._next_month
        )
        next_btn.pack(side="right")

        # Quick shortcuts row
        quick_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        quick_frame.pack(fill="x", padx=12, pady=(0, 8))

        quick_tmrw = ctk.CTkButton(
            quick_frame,
            text="Tomorrow",
            height=26,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            fg_color=("#E0F2FE", "#0C4A6E"),
            text_color=("#0369A1", "#7DD3FC"),
            hover_color=("#BAE6FD", "#075985"),
            command=lambda: self._select_date(self.min_date)
        )
        quick_tmrw.pack(side="left", padx=(0, 6), expand=True, fill="x")

        in_3_days = self.today + datetime.timedelta(days=3)
        quick_3d = ctk.CTkButton(
            quick_frame,
            text="+3 Days",
            height=26,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            fg_color=("#F1F5F9", "#334155"),
            text_color=("#475569", "#CBD5E1"),
            hover_color=("#E2E8F0", "#475569"),
            command=lambda: self._select_date(in_3_days)
        )
        quick_3d.pack(side="left", padx=(0, 6), expand=True, fill="x")

        in_1_week = self.today + datetime.timedelta(days=7)
        quick_1w = ctk.CTkButton(
            quick_frame,
            text="+1 Week",
            height=26,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            fg_color=("#F1F5F9", "#334155"),
            text_color=("#475569", "#CBD5E1"),
            hover_color=("#E2E8F0", "#475569"),
            command=lambda: self._select_date(in_1_week)
        )
        quick_1w.pack(side="left", expand=True, fill="x")

        # Days of Week Header (Mon - Sun)
        dow_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        dow_frame.pack(fill="x", padx=12, pady=(4, 2))
        for col_idx, day_name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            lbl = ctk.CTkLabel(
                dow_frame,
                text=day_name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#94A3B8", "#64748B"),
                width=40
            )
            lbl.grid(row=0, column=col_idx, padx=2)

        # Calendar Grid container
        self.grid_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=12, pady=(2, 10))

        self._render_calendar()

    def _render_calendar(self) -> None:
        """Draw the day buttons for current month view."""
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        month_name = calendar.month_name[self.view_month]
        self.month_year_label.configure(text=f"{month_name} {self.view_year}")

        cal = calendar.monthcalendar(self.view_year, self.view_month)

        for row_idx, week in enumerate(cal):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue

                curr_d = datetime.date(self.view_year, self.view_month, day)
                is_disabled = (curr_d < self.min_date or curr_d > self.max_date)
                is_selected = (curr_d == self.selected_date)

                if is_selected:
                    btn_fg = COLORS["primary"]
                    btn_text = "#FFFFFF"
                    btn_hover = COLORS["primary_hover"]
                elif is_disabled:
                    btn_fg = ("#F8FAFC", "#0F172A")
                    btn_text = ("#CBD5E1", "#475569")
                    btn_hover = btn_fg
                else:
                    btn_fg = ("#F1F5F9", "#334155")
                    btn_text = ("#0F172A", "#F8FAFC")
                    btn_hover = ("#E2E8F0", "#475569")

                btn = ctk.CTkButton(
                    self.grid_frame,
                    text=str(day),
                    width=38,
                    height=32,
                    corner_radius=8,
                    font=ctk.CTkFont(size=12, weight="bold" if is_selected else "normal"),
                    fg_color=btn_fg,
                    text_color=btn_text,
                    hover_color=btn_hover,
                    state="disabled" if is_disabled else "normal",
                    command=lambda d=curr_d: self._select_date(d)
                )
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)

    def _prev_month(self) -> None:
        if self.view_month == 1:
            self.view_month = 12
            self.view_year -= 1
        else:
            self.view_month -= 1
        self._render_calendar()

    def _next_month(self) -> None:
        if self.view_month == 12:
            self.view_month = 1
            self.view_year += 1
        else:
            self.view_month += 1
        self._render_calendar()

    def _select_date(self, selected_d: datetime.date) -> None:
        self.selected_date = selected_d
        formatted = selected_d.strftime("%Y-%m-%d")
        if self.on_date_selected:
            self.on_date_selected(formatted)
        self.destroy()

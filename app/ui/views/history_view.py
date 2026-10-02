"""
Patient Appointment History View for Medicare Specialist Portal.
Displays a structured list/table of all appointments booked by the patient
with real-time status pill badges and search filtering.
"""

import customtkinter as ctk
from typing import Callable, Dict, Any, List, Optional
from app.config import (
    COLORS,
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_REJECTED
)
from app.services.appointment_service import AppointmentService
from app.ui.components.header_bar import HeaderBar
from app.ui.components.status_badge import StatusBadge

class HistoryView(ctk.CTkFrame):
    """
    Shows all previous and upcoming bookings for the logged-in patient.
    """
    def __init__(
        self,
        master,
        user_info: Dict[str, Any],
        appointment_service: AppointmentService,
        on_back_to_booking: Callable[[], None],
        on_logout: Callable[[], None],
        show_toast: Callable[[str, str], None],
        **kwargs
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0B132B"), **kwargs)
        self.user_info = user_info
        self.appointment_service = appointment_service
        self.on_back_to_booking = on_back_to_booking
        self.on_logout = on_logout
        self.show_toast = show_toast

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self) -> None:
        # Header Bar
        self.header = HeaderBar(
            self,
            user_info=self.user_info,
            on_logout=self.on_logout
        )
        self.header.grid(row=0, column=0, sticky="ew")

        # Main Container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Toolbar / Header Action Strip
        toolbar = ctk.CTkFrame(main_container, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        back_btn = ctk.CTkButton(
            toolbar,
            text="← Back to Booking Portal",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color=("#E0F2FE", "#0C4A6E"),
            text_color=("#0369A1", "#7DD3FC"),
            hover_color=("#BAE6FD", "#075985"),
            command=self.on_back_to_booking
        )
        back_btn.pack(side="left")

        # Title in center / left
        title_box = ctk.CTkFrame(toolbar, fg_color="transparent")
        title_box.pack(side="left", padx=16)

        title_lbl = ctk.CTkLabel(
            title_box,
            text="My Consultation History",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        title_lbl.pack(anchor="w")

        # Search box
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Search by Doctor, Location, or Date...",
            width=260,
            height=38,
            corner_radius=10,
            fg_color=("#FFFFFF", "#1C2541"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(side="right", padx=(8, 0))
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_records())

        # Refresh button
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Refresh",
            width=85,
            height=38,
            corner_radius=10,
            fg_color=("#F1F5F9", "#243256"),
            hover_color=("#E2E8F0", "#3A506B"),
            text_color=("#334155", "#CBD5E1"),
            command=self.refresh_records
        )
        refresh_btn.pack(side="right")

        # Scrollable Record Cards Container
        self.cards_scroll = ctk.CTkScrollableFrame(
            main_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.cards_scroll.grid(row=1, column=0, sticky="nsew")
        self.cards_scroll.grid_columnconfigure(0, weight=1)

        self.refresh_records()

    def refresh_records(self) -> None:
        """Fetch records from database and render cards."""
        for widget in self.cards_scroll.winfo_children():
            widget.destroy()

        search_q = self.search_entry.get().strip() if hasattr(self, "search_entry") else None
        username = self.user_info.get("username", "")
        records = self.appointment_service.get_patient_appointments(username, search_q)

        if not records:
            # Render Empty State
            empty_frame = ctk.CTkFrame(
                self.cards_scroll,
                corner_radius=16,
                fg_color=("#FFFFFF", "#1C2541"),
                border_width=1,
                border_color=("#E2E8F0", "#3A506B")
            )
            empty_frame.pack(fill="both", expand=True, padx=20, pady=40)

            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📋",
                font=ctk.CTkFont(size=48)
            )
            empty_icon.pack(pady=(36, 12))

            empty_title = ctk.CTkLabel(
                empty_frame,
                text="No Appointments Found",
                font=ctk.CTkFont(size=17, weight="bold"),
                text_color=("#0F172A", "#F8FAFC")
            )
            empty_title.pack()

            empty_sub = ctk.CTkLabel(
                empty_frame,
                text="You haven't scheduled any specialist consultations yet, or no records matched your search query.",
                font=ctk.CTkFont(size=12),
                text_color=("#64748B", "#94A3B8")
            )
            empty_sub.pack(pady=(6, 20))

            book_now_btn = ctk.CTkButton(
                empty_frame,
                text="📅 Schedule First Appointment",
                height=38,
                corner_radius=8,
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=self.on_back_to_booking
            )
            book_now_btn.pack(pady=(0, 36))
            return

        # Render each appointment as a modern elevated card
        for item in records:
            self._render_appointment_card(item)

    def _render_appointment_card(self, app: Dict[str, Any]) -> None:
        card = ctk.CTkFrame(
            self.cards_scroll,
            corner_radius=14,
            border_width=1,
            fg_color=("#FFFFFF", "#1C2541"),
            border_color=("#E2E8F0", "#3A506B")
        )
        card.pack(fill="x", padx=4, pady=6)
        card.grid_columnconfigure(1, weight=1)

        # Left status indicator stripe / icon
        status = app.get("status", STATUS_PENDING)
        accent_color = COLORS["accent"] if status == STATUS_CONFIRMED else (COLORS["danger"] if status == STATUS_REJECTED else COLORS["warning"])

        if status == STATUS_CONFIRMED:
            badge_bg = ("#D1FAE5", "#064E3B")
        elif status == STATUS_REJECTED:
            badge_bg = ("#FEE2E2", "#7F1D1D")
        else:
            badge_bg = ("#FEF3C7", "#451A03")

        left_badge = ctk.CTkFrame(
            card,
            width=50,
            height=50,
            corner_radius=12,
            fg_color=badge_bg
        )
        left_badge.grid(row=0, column=0, rowspan=2, padx=16, pady=16)

        icon_char = "✓" if status == STATUS_CONFIRMED else ("✕" if status == STATUS_REJECTED else "⏳")
        icon_lbl = ctk.CTkLabel(
            left_badge,
            text=icon_char,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=accent_color
        )
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # Center Main Details
        center_frame = ctk.CTkFrame(card, fg_color="transparent")
        center_frame.grid(row=0, column=1, padx=(0, 16), pady=(14, 4), sticky="w")

        top_row = ctk.CTkFrame(center_frame, fg_color="transparent")
        top_row.pack(fill="x")

        doc_lbl = ctk.CTkLabel(
            top_row,
            text=f"👨‍⚕️ {app.get('doctor_name', 'Doctor')}",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        doc_lbl.pack(side="left")

        ref_lbl = ctk.CTkLabel(
            top_row,
            text=f" • Ref: #{app.get('id', '0')}",
            font=ctk.CTkFont(size=12),
            text_color=("#94A3B8", "#64748B")
        )
        ref_lbl.pack(side="left")

        # Patient & Contact info
        patient_lbl = ctk.CTkLabel(
            center_frame,
            text=f"Patient: {app.get('patient_name', '')}  |  Contact: {app.get('contact_number', '')}",
            font=ctk.CTkFont(size=12),
            text_color=("#475569", "#CBD5E1"),
            anchor="w"
        )
        patient_lbl.pack(fill="x", pady=(2, 2))

        # Date & Slot & Location
        loc_row = ctk.CTkFrame(card, fg_color="transparent")
        loc_row.grid(row=1, column=1, padx=(0, 16), pady=(0, 14), sticky="w")

        date_pill = ctk.CTkLabel(
            loc_row,
            text=f"📅 {app.get('app_date', '')} ({app.get('app_time_slot', '')})",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0369A1", "#38BDF8")
        )
        date_pill.pack(side="left", padx=(0, 16))

        clinic_lbl = ctk.CTkLabel(
            loc_row,
            text=f"📍 {app.get('clinic_address', '')}",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        clinic_lbl.pack(side="left")

        # Right Status Pill
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.grid(row=0, column=2, rowspan=2, padx=16, pady=16, sticky="e")

        status_badge = StatusBadge(right_frame, status=status)
        status_badge.pack(anchor="e")

"""
Patient Appointment Booking Dashboard for Medicare Specialist Portal.
Features interactive booking form, dynamic real-time clinic address card,
future-date calendar picker, and direct history routing.
"""

import datetime
import customtkinter as ctk
from typing import Callable, Dict, Any, Optional
from app.config import (
    DOCTOR_LIST,
    DOCTOR_SCHEDULE_MATRIX,
    TIME_SLOTS,
    COLORS
)
from app.services.appointment_service import AppointmentService
from app.services.validation_service import ValidationService
from app.ui.components.header_bar import HeaderBar
from app.ui.components.date_picker import CalendarDatePickerDialog

class PatientView(ctk.CTkFrame):
    """
    Patient dashboard offering appointment booking with real-time branch matrix lookup.
    """
    def __init__(
        self,
        master,
        user_info: Dict[str, Any],
        appointment_service: AppointmentService,
        on_view_history: Callable[[], None],
        on_logout: Callable[[], None],
        show_toast: Callable[[str, str], None],
        **kwargs
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0B132B"), **kwargs)
        self.user_info = user_info
        self.appointment_service = appointment_service
        self.on_view_history = on_view_history
        self.on_logout = on_logout
        self.show_toast = show_toast

        # Calculate tomorrow's date for initial default
        self.tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self) -> None:
        # Top Header Bar
        self.header = HeaderBar(
            self,
            user_info=self.user_info,
            on_logout=self.on_logout
        )
        self.header.grid(row=0, column=0, sticky="ew")

        # Main Scrollable Content Container
        self.content_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.content_scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self.content_scroll.grid_columnconfigure(0, weight=3) # Form column
        self.content_scroll.grid_columnconfigure(1, weight=2) # Dynamic Clinic Info column

        # Section Top Banner / Action Strip
        banner_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        banner_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        intro_box = ctk.CTkFrame(banner_frame, fg_color="transparent")
        intro_box.pack(side="left")

        page_title = ctk.CTkLabel(
            intro_box,
            text="Book a Specialist Consultation",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        page_title.pack(anchor="w")

        page_sub = ctk.CTkLabel(
            intro_box,
            text="Schedule an in-person appointment with our specialist physicians across Mangalore clinics.",
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8")
        )
        page_sub.pack(anchor="w", pady=(2, 0))

        # "My Appointments" Button
        history_btn = ctk.CTkButton(
            banner_frame,
            text="📋 My Appointments History ➜",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color=("#E0F2FE", "#0C4A6E"),
            text_color=("#0369A1", "#7DD3FC"),
            hover_color=("#BAE6FD", "#075985"),
            command=self.on_view_history
        )
        history_btn.pack(side="right")

        # ================= LEFT COLUMN: BOOKING FORM CARD =================
        self.form_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=18,
            border_width=1,
            fg_color=("#FFFFFF", "#1C2541"),
            border_color=("#E2E8F0", "#3A506B")
        )
        self.form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=0)

        self._build_form_card()

        # ================= RIGHT COLUMN: DYNAMIC CLINIC CARD =================
        self.clinic_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=18,
            border_width=1,
            fg_color=("#FFFFFF", "#1C2541"),
            border_color=("#E2E8F0", "#3A506B")
        )
        self.clinic_card.grid(row=1, column=1, sticky="nsew", padx=(12, 0), pady=0)

        self._build_dynamic_clinic_card()

        # Trigger initial clinic card update
        self._on_selection_change()

    def _build_form_card(self) -> None:
        card = self.form_card

        # Card Title
        form_heading = ctk.CTkLabel(
            card,
            text="📝 Patient & Appointment Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        form_heading.pack(fill="x", padx=24, pady=(20, 16))

        # 1. Patient Full Name
        name_lbl = ctk.CTkLabel(
            card,
            text="Patient Full Name *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        name_lbl.pack(fill="x", padx=24, pady=(0, 4))

        self.name_entry = ctk.CTkEntry(
            card,
            placeholder_text="e.g. Rahul Verma (letters and spaces only)",
            height=38,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.name_entry.pack(fill="x", padx=24, pady=(0, 2))
        # Prefill if username looks like a name
        default_name = self.user_info.get("username", "").replace("_", " ").title()
        if default_name and default_name.lower() != "admin":
            self.name_entry.insert(0, default_name)

        name_hint = ctk.CTkLabel(
            card,
            text="* Letters and spaces only (no symbols or numbers)",
            font=ctk.CTkFont(size=10),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        name_hint.pack(fill="x", padx=24, pady=(0, 12))

        # 2. Contact Number
        contact_lbl = ctk.CTkLabel(
            card,
            text="Contact Number *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        contact_lbl.pack(fill="x", padx=24, pady=(0, 4))

        self.contact_entry = ctk.CTkEntry(
            card,
            placeholder_text="+91 9845123456",
            height=38,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.contact_entry.insert(0, "+91 ")
        self.contact_entry.pack(fill="x", padx=24, pady=(0, 2))
        self.contact_entry.bind("<KeyRelease>", self._on_contact_key_release)

        contact_hint = ctk.CTkLabel(
            card,
            text="* Exactly 10 digits prefixed with +91 (e.g. +91 9876543210)",
            font=ctk.CTkFont(size=10),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        contact_hint.pack(fill="x", padx=24, pady=(0, 12))

        # 3. Doctor Selector Dropdown
        doc_lbl = ctk.CTkLabel(
            card,
            text="Specialist Doctor *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        doc_lbl.pack(fill="x", padx=24, pady=(0, 4))

        self.doc_dropdown = ctk.CTkOptionMenu(
            card,
            values=DOCTOR_LIST,
            height=38,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=("#0F172A", "#F8FAFC"),
            dropdown_fg_color=("#FFFFFF", "#1E293B"),
            dropdown_text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda val: self._on_selection_change()
        )
        self.doc_dropdown.set(DOCTOR_LIST[0])
        self.doc_dropdown.pack(fill="x", padx=24, pady=(0, 14))

        # 4. Time Slot Dropdown
        slot_lbl = ctk.CTkLabel(
            card,
            text="Consultation Time Slot *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        slot_lbl.pack(fill="x", padx=24, pady=(0, 4))

        self.slot_dropdown = ctk.CTkOptionMenu(
            card,
            values=TIME_SLOTS,
            height=38,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=("#0F172A", "#F8FAFC"),
            dropdown_fg_color=("#FFFFFF", "#1E293B"),
            dropdown_text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda val: self._on_selection_change()
        )
        self.slot_dropdown.set(TIME_SLOTS[0])
        self.slot_dropdown.pack(fill="x", padx=24, pady=(0, 14))

        # 5. Appointment Date with Calendar Picker
        date_lbl = ctk.CTkLabel(
            card,
            text="Appointment Date (Must be Tomorrow or Later) *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        date_lbl.pack(fill="x", padx=24, pady=(0, 4))

        date_row = ctk.CTkFrame(card, fg_color="transparent")
        date_row.pack(fill="x", padx=24, pady=(0, 2))

        self.date_entry = ctk.CTkEntry(
            date_row,
            placeholder_text="YYYY-MM-DD",
            height=38,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.date_entry.insert(0, self.tomorrow_str)
        self.date_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.calendar_btn = ctk.CTkButton(
            date_row,
            text="📅 Select Date",
            width=120,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#E0F2FE", "#0C4A6E"),
            text_color=("#0369A1", "#7DD3FC"),
            hover_color=("#BAE6FD", "#075985"),
            command=self._open_date_picker
        )
        self.calendar_btn.pack(side="right")

        date_hint = ctk.CTkLabel(
            card,
            text="* Dates must be in the future (minimum tomorrow)",
            font=ctk.CTkFont(size=10),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        date_hint.pack(fill="x", padx=24, pady=(0, 20))

        # Submit Appointment Button
        self.submit_btn = ctk.CTkButton(
            card,
            text="✓ Confirm & Schedule Appointment",
            height=44,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            command=self._handle_booking_submit
        )
        self.submit_btn.pack(fill="x", padx=24, pady=(0, 24))

    def _build_dynamic_clinic_card(self) -> None:
        card = self.clinic_card

        # Header Badge
        header_box = ctk.CTkFrame(card, fg_color="transparent")
        header_box.pack(fill="x", padx=20, pady=(20, 12))

        loc_icon = ctk.CTkLabel(
            header_box,
            text="📍",
            font=ctk.CTkFont(size=20),
            width=36,
            height=36,
            corner_radius=10,
            fg_color=("#E0F2FE", "#0C4A6E")
        )
        loc_icon.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(header_box, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)

        self.clinic_card_title = ctk.CTkLabel(
            title_box,
            text="Branch Schedule & Location",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        self.clinic_card_title.pack(anchor="w")

        self.clinic_card_sub = ctk.CTkLabel(
            title_box,
            text="Live branch matrix resolution",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        self.clinic_card_sub.pack(anchor="w")

        # Dynamic Details Container
        self.details_container = ctk.CTkFrame(
            card,
            corner_radius=12,
            fg_color=("#F8FAFC", "#0E1838"),
            border_width=1,
            border_color=("#E2E8F0", "#3A506B")
        )
        self.details_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Doctor Profile Banner
        self.doc_name_label = ctk.CTkLabel(
            self.details_container,
            text="Dr. Sharma",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["primary_text"],
            anchor="w"
        )
        self.doc_name_label.pack(fill="x", padx=16, pady=(16, 2))

        self.doc_exp_label = ctk.CTkLabel(
            self.details_container,
            text="Specialty & Credentials",
            font=ctk.CTkFont(size=11),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        self.doc_exp_label.pack(fill="x", padx=16, pady=(0, 12))

        # Branch Pill Container
        self.branch_pill = ctk.CTkFrame(
            self.details_container,
            corner_radius=8,
            fg_color=("#E0F2FE", "#0C4A6E"),
            border_width=1,
            border_color=("#BAE6FD", "#0369A1")
        )
        self.branch_pill.pack(fill="x", padx=16, pady=(0, 12))

        self.branch_name_label = ctk.CTkLabel(
            self.branch_pill,
            text="Surathkal Branch",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#0369A1", "#7DD3FC"),
            anchor="w"
        )
        self.branch_name_label.pack(fill="x", padx=12, pady=6)

        # Address Box
        addr_title = ctk.CTkLabel(
            self.details_container,
            text="🏥 CLINIC ADDRESS:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        addr_title.pack(fill="x", padx=16, pady=(0, 2))

        self.address_label = ctk.CTkLabel(
            self.details_container,
            text="NH 66, Near NITK Main Gate...",
            font=ctk.CTkFont(size=12),
            text_color=("#334155", "#CBD5E1"),
            anchor="w",
            justify="left",
            wraplength=280
        )
        self.address_label.pack(fill="x", padx=16, pady=(0, 10))

        # Room & Suite Box
        room_title = ctk.CTkLabel(
            self.details_container,
            text="🚪 ROOM / SUITE:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        room_title.pack(fill="x", padx=16, pady=(0, 2))

        self.room_label = ctk.CTkLabel(
            self.details_container,
            text="Cardiology Suite A-101",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        self.room_label.pack(fill="x", padx=16, pady=(0, 10))

        # Direct Branch Contact
        phone_title = ctk.CTkLabel(
            self.details_container,
            text="📞 BRANCH DESK HELPLINE:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        phone_title.pack(fill="x", padx=16, pady=(0, 2))

        self.phone_label = ctk.CTkLabel(
            self.details_container,
            text="+91 824 2474000",
            font=ctk.CTkFont(size=12),
            text_color=("#0369A1", "#38BDF8"),
            anchor="w"
        )
        self.phone_label.pack(fill="x", padx=16, pady=(0, 16))

        # Status note
        note_pill = ctk.CTkFrame(
            self.details_container,
            corner_radius=8,
            fg_color=("#FEF3C7", "#451A03")
        )
        note_pill.pack(fill="x", padx=16, pady=(0, 16))

        note_lbl = ctk.CTkLabel(
            note_pill,
            text="⚡ Status starts as 'Pending' until reviewed by hospital administration.",
            font=ctk.CTkFont(size=11),
            text_color=("#B45309", "#FCD34D"),
            wraplength=260,
            justify="left"
        )
        note_lbl.pack(padx=10, pady=8)

    # ================= INTERACTIONS & LOGIC =================

    def _on_selection_change(self) -> None:
        """Triggered when doctor or time slot selection changes."""
        selected_doc = self.doc_dropdown.get()
        selected_slot = self.slot_dropdown.get()

        info = AppointmentService.get_clinic_info(selected_doc, selected_slot)
        doc_matrix = DOCTOR_SCHEDULE_MATRIX.get(selected_doc, {})

        if info and doc_matrix:
            self.doc_name_label.configure(text=f"👨‍⚕️ {selected_doc}")
            self.doc_exp_label.configure(text=f"{doc_matrix.get('specialty', '')} • {doc_matrix.get('experience', '')}")
            self.branch_name_label.configure(text=f"🏥 {info.get('branch', 'Branch Location')}")
            self.address_label.configure(text=info.get("address", "Address unavailable"))
            self.room_label.configure(text=info.get("room", "General OPD"))
            self.phone_label.configure(text=info.get("phone", "+91 824 2000000"))

    def _on_contact_key_release(self, event=None) -> None:
        """Helper to ensure +91 prefix stays intact and only digits are appended."""
        val = self.contact_entry.get()
        formatted = ValidationService.format_contact_number(val)
        if val != formatted and len(val) > len(formatted):
            self.contact_entry.delete(0, "end")
            self.contact_entry.insert(0, formatted)

    def _open_date_picker(self) -> None:
        """Opens modern calendar modal dialog."""
        current_val = self.date_entry.get()
        CalendarDatePickerDialog(
            self,
            current_date_str=current_val,
            on_date_selected=self._on_date_selected
        )

    def _on_date_selected(self, date_str: str) -> None:
        """Callback from calendar picker."""
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date_str)
        self.show_toast(f"Date set to {date_str}", "info")

    def _handle_booking_submit(self) -> None:
        patient_name = self.name_entry.get()
        contact_number = self.contact_entry.get()
        doctor_name = self.doc_dropdown.get()
        time_slot = self.slot_dropdown.get()
        app_date = self.date_entry.get()
        booked_by = self.user_info.get("username", "patient")

        success, app_id, msg = self.appointment_service.book_appointment(
            patient_name=patient_name,
            contact_number=contact_number,
            doctor_name=doctor_name,
            time_slot=time_slot,
            app_date=app_date,
            booked_by=booked_by
        )

        if success:
            self.show_toast(msg, "success")
            # Navigate to History screen after booking so patient can see their new pending appointment
            self.after(1200, self.on_view_history)
        else:
            self.show_toast(msg, "error")

"""
Admin Control Center View for Medicare Specialist Portal.
Provides comprehensive appointment filtering, live KPI statistics,
status review workflow (Accept / Reject), and reporting.
"""

import csv
import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from typing import Callable, Dict, Any, List, Optional
from app.config import (
    COLORS,
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_REJECTED,
    DOCTOR_LIST
)
from app.services.appointment_service import AppointmentService
from app.ui.components.header_bar import HeaderBar
from app.ui.components.status_badge import StatusBadge
from app.ui.components.stat_card import StatCard
from app.ui.components.modal import ConfirmationModal

class AdminView(ctk.CTkFrame):
    """
    Admin Command Center with real-time analytics, filtering, and action buttons.
    """
    def __init__(
        self,
        master,
        user_info: Dict[str, Any],
        appointment_service: AppointmentService,
        on_logout: Callable[[], None],
        show_toast: Callable[[str, str], None],
        **kwargs
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0B132B"), **kwargs)
        self.user_info = user_info
        self.appointment_service = appointment_service
        self.on_logout = on_logout
        self.show_toast = show_toast

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self) -> None:
        # 1. Header Bar
        self.header = HeaderBar(
            self,
            user_info=self.user_info,
            on_logout=self.on_logout
        )
        self.header.grid(row=0, column=0, sticky="ew")

        # 2. Main Scrollable Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self.main_container.grid_rowconfigure(2, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 3. Top KPI Metric Cards Grid
        self._build_stats_section()

        # 4. Filter Toolbar
        self._build_toolbar_section()

        # 5. Table Container
        self._build_table_section()

        # Initial data load
        self.refresh_data()

    def _build_stats_section(self) -> None:
        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        for col in range(5):
            stats_frame.grid_columnconfigure(col, weight=1)

        # 5 Metric Cards
        self.card_total = StatCard(
            stats_frame,
            title="TOTAL BOOKINGS",
            value="0",
            icon="📊",
            accent_color=COLORS["primary"],
            subtitle="All recorded slots"
        )
        self.card_total.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_pending = StatCard(
            stats_frame,
            title="PENDING REVIEW",
            value="0",
            icon="⏳",
            accent_color=COLORS["warning"],
            subtitle="Requires action"
        )
        self.card_pending.grid(row=0, column=1, padx=(0, 8), sticky="ew")

        self.card_confirmed = StatCard(
            stats_frame,
            title="CONFIRMED",
            value="0",
            icon="✓",
            accent_color=COLORS["accent"],
            subtitle="Approved consultations"
        )
        self.card_confirmed.grid(row=0, column=2, padx=(0, 8), sticky="ew")

        self.card_rejected = StatCard(
            stats_frame,
            title="REJECTED",
            value="0",
            icon="✕",
            accent_color=COLORS["danger"],
            subtitle="Declined / Cancelled"
        )
        self.card_rejected.grid(row=0, column=3, padx=(0, 8), sticky="ew")

        self.card_today = StatCard(
            stats_frame,
            title="TODAY'S SCHEDULE",
            value="0",
            icon="📅",
            accent_color="#8B5CF6", # Purple accent
            subtitle="Appointments today"
        )
        self.card_today.grid(row=0, column=4, padx=(0, 0), sticky="ew")

    def _build_toolbar_section(self) -> None:
        toolbar = ctk.CTkFrame(
            self.main_container,
            corner_radius=12,
            border_width=1,
            fg_color=("#FFFFFF", "#1C2541"),
            border_color=("#E2E8F0", "#3A506B")
        )
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        # Search Bar
        search_icon_lbl = ctk.CTkLabel(
            toolbar,
            text="🔍",
            font=ctk.CTkFont(size=14)
        )
        search_icon_lbl.pack(side="left", padx=(14, 4), pady=10)

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search patient, contact, doctor, clinic, ID...",
            width=280,
            height=36,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=12)
        )
        self.search_entry.pack(side="left", padx=(0, 14), pady=10)
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_table())

        # Status Filter Dropdown
        status_lbl = ctk.CTkLabel(
            toolbar,
            text="Status:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8")
        )
        status_lbl.pack(side="left", padx=(0, 6), pady=10)

        self.status_filter_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["All", STATUS_PENDING, STATUS_CONFIRMED, STATUS_REJECTED],
            width=120,
            height=36,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=("#0F172A", "#F8FAFC"),
            dropdown_fg_color=("#FFFFFF", "#1E293B"),
            dropdown_text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=12),
            command=lambda val: self.refresh_table()
        )
        self.status_filter_menu.set("All")
        self.status_filter_menu.pack(side="left", padx=(0, 14), pady=10)

        # Doctor Filter Dropdown
        doc_lbl = ctk.CTkLabel(
            toolbar,
            text="Doctor:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8")
        )
        doc_lbl.pack(side="left", padx=(0, 6), pady=10)

        self.doctor_filter_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["All Doctors"] + DOCTOR_LIST,
            width=200,
            height=36,
            corner_radius=8,
            fg_color=("#F8FAFC", "#0E1838"),
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            text_color=("#0F172A", "#F8FAFC"),
            dropdown_fg_color=("#FFFFFF", "#1E293B"),
            dropdown_text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=12),
            command=lambda val: self.refresh_table()
        )
        self.doctor_filter_menu.set("All Doctors")
        self.doctor_filter_menu.pack(side="left", padx=(0, 14), pady=10)

        # Right Action Buttons (Export CSV & Refresh)
        export_btn = ctk.CTkButton(
            toolbar,
            text="📥 Export CSV",
            height=36,
            width=110,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#E0F2FE", "#0C4A6E"),
            text_color=("#0369A1", "#7DD3FC"),
            hover_color=("#BAE6FD", "#075985"),
            command=self._export_to_csv
        )
        export_btn.pack(side="right", padx=(8, 14), pady=10)

        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Refresh",
            height=36,
            width=90,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#F1F5F9", "#243256"),
            hover_color=("#E2E8F0", "#3A506B"),
            text_color=("#334155", "#CBD5E1"),
            command=self.refresh_data
        )
        refresh_btn.pack(side="right", pady=10)

    def _build_table_section(self) -> None:
        self.table_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=16,
            border_width=1,
            fg_color=("#FFFFFF", "#1C2541"),
            border_color=("#E2E8F0", "#3A506B")
        )
        self.table_card.grid(row=2, column=0, sticky="nsew")
        self.table_card.grid_rowconfigure(1, weight=1)
        self.table_card.grid_columnconfigure(0, weight=1)

        # Table Header Bar
        tbl_header = ctk.CTkFrame(
            self.table_card,
            height=40,
            corner_radius=8,
            fg_color=("#F1F5F9", "#172038")
        )
        tbl_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))

        headers = [
            ("ID", 50),
            ("Patient Name & Contact", 220),
            ("Doctor & Specialty", 200),
            ("Date & Time Slot", 160),
            ("Clinic Location", 180),
            ("Status", 110),
            ("Quick Review Actions", 180),
        ]

        for idx, (title, width) in enumerate(headers):
            lbl = ctk.CTkLabel(
                tbl_header,
                text=title.upper(),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#64748B", "#94A3B8"),
                anchor="w" if idx > 0 and idx < 6 else ("center" if idx == 0 or idx == 6 else "w"),
                width=width
            )
            lbl.pack(side="left", padx=6, pady=8)

        # Scrollable Rows Container
        self.rows_scroll = ctk.CTkScrollableFrame(
            self.table_card,
            fg_color="transparent",
            corner_radius=0
        )
        self.rows_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.rows_scroll.grid_columnconfigure(0, weight=1)

    # ================= DATA REFRESH & RENDERING =================

    def refresh_data(self) -> None:
        """Refreshes KPI metrics and appointment table."""
        self._refresh_stats()
        self.refresh_table()

    def _refresh_stats(self) -> None:
        stats = self.appointment_service.get_dashboard_stats()
        self.card_total.update_value(stats["total"])
        self.card_pending.update_value(stats["pending"])
        self.card_confirmed.update_value(stats["confirmed"])
        self.card_rejected.update_value(stats["rejected"])
        self.card_today.update_value(stats["today"])

    def refresh_table(self) -> None:
        """Fetch filtered appointments and render table rows."""
        for widget in self.rows_scroll.winfo_children():
            widget.destroy()

        search_q = self.search_entry.get().strip() if hasattr(self, "search_entry") else None
        status_val = self.status_filter_menu.get() if hasattr(self, "status_filter_menu") else "All"
        doc_val = self.doctor_filter_menu.get() if hasattr(self, "doctor_filter_menu") else "All Doctors"

        records = self.appointment_service.get_all_appointments(
            search_query=search_q,
            status_filter=status_val,
            doctor_filter=doc_val
        )

        if not records:
            empty_lbl = ctk.CTkLabel(
                self.rows_scroll,
                text="No appointments match the current filter criteria.",
                font=ctk.CTkFont(size=13),
                text_color=("#94A3B8", "#64748B")
            )
            empty_lbl.pack(pady=40)
            return

        for idx, app in enumerate(records):
            self._render_table_row(app, idx)

    def _render_table_row(self, app: Dict[str, Any], row_idx: int) -> None:
        is_even = (row_idx % 2 == 0)
        row_bg = ("#FFFFFF", "#1C2541") if is_even else ("#F8FAFC", "#172038")

        row_frame = ctk.CTkFrame(
            self.rows_scroll,
            height=54,
            corner_radius=8,
            fg_color=row_bg,
            border_width=1,
            border_color=("#F1F5F9", "#243256")
        )
        row_frame.pack(fill="x", pady=2)
        row_frame.pack_propagate(False)

        app_id = app.get("id", 0)
        status = app.get("status", STATUS_PENDING)
        is_pending = (status == STATUS_PENDING)

        # 1. ID
        id_lbl = ctk.CTkLabel(
            row_frame,
            text=f"#{app_id}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            width=50,
            anchor="center"
        )
        id_lbl.pack(side="left", padx=6)

        # 2. Patient & Contact
        p_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=220)
        p_box.pack(side="left", padx=6)
        p_box.pack_propagate(False)

        p_name = ctk.CTkLabel(
            p_box,
            text=app.get("patient_name", ""),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        p_name.pack(fill="x")

        p_contact = ctk.CTkLabel(
            p_box,
            text=f"📞 {app.get('contact_number', '')} • by {app.get('booked_by', '')}",
            font=ctk.CTkFont(size=10),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        p_contact.pack(fill="x")

        # 3. Doctor
        d_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=200)
        d_box.pack(side="left", padx=6)
        d_box.pack_propagate(False)

        d_name = ctk.CTkLabel(
            d_box,
            text=app.get("doctor_name", ""),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#0369A1", "#38BDF8"),
            anchor="w"
        )
        d_name.pack(fill="x")

        # 4. Date & Slot
        slot_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=160)
        slot_box.pack(side="left", padx=6)
        slot_box.pack_propagate(False)

        d_date = ctk.CTkLabel(
            slot_box,
            text=f"📅 {app.get('app_date', '')}",
            font=ctk.CTkFont(size=12),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        d_date.pack(fill="x")

        d_slot = ctk.CTkLabel(
            slot_box,
            text=app.get("app_time_slot", ""),
            font=ctk.CTkFont(size=10),
            text_color=("#64748B", "#94A3B8"),
            anchor="w"
        )
        d_slot.pack(fill="x")

        # 5. Clinic Address
        loc_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=180)
        loc_box.pack(side="left", padx=6)
        loc_box.pack_propagate(False)

        # Extract branch name if present
        full_addr = app.get("clinic_address", "")
        branch_name = full_addr.split(",")[0] if "," in full_addr else full_addr

        loc_lbl = ctk.CTkLabel(
            loc_box,
            text=f"📍 {branch_name}",
            font=ctk.CTkFont(size=11),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        loc_lbl.pack(fill="x")

        # 6. Status Badge
        badge_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=110)
        badge_box.pack(side="left", padx=6)
        badge_box.pack_propagate(False)

        badge = StatusBadge(badge_box, status=status)
        badge.pack(anchor="w", pady=10)

        # 7. Action Buttons (Accept & Reject)
        actions_box = ctk.CTkFrame(row_frame, fg_color="transparent", width=180)
        actions_box.pack(side="left", padx=6)
        actions_box.pack_propagate(False)

        if is_pending:
            accept_btn = ctk.CTkButton(
                actions_box,
                text="✓ Accept",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=75,
                height=30,
                corner_radius=6,
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color="#FFFFFF",
                command=lambda a_id=app_id: self._handle_accept(a_id)
            )
            accept_btn.pack(side="left", padx=(0, 6), pady=12)

            reject_btn = ctk.CTkButton(
                actions_box,
                text="✕ Reject",
                font=ctk.CTkFont(size=11, weight="bold"),
                width=75,
                height=30,
                corner_radius=6,
                fg_color=COLORS["danger"],
                hover_color=COLORS["danger_hover"],
                text_color="#FFFFFF",
                command=lambda a_id=app_id: self._handle_reject(a_id)
            )
            reject_btn.pack(side="left", pady=12)
        else:
            # Disabled pill showing action already completed
            locked_lbl = ctk.CTkLabel(
                actions_box,
                text=f"🔒 {status}",
                font=ctk.CTkFont(size=11),
                text_color=("#94A3B8", "#64748B"),
                anchor="center"
            )
            locked_lbl.pack(fill="both", expand=True, pady=12)

    # ================= STATUS WORKFLOW ACTIONS =================

    def _handle_accept(self, appointment_id: int) -> None:
        """Accepts an appointment (sets status to Confirmed)."""
        success, msg = self.appointment_service.update_status(appointment_id, STATUS_CONFIRMED)
        if success:
            self.show_toast(f"✓ Appointment #{appointment_id} confirmed!", "success")
            self.refresh_data()
        else:
            self.show_toast(msg, "error")

    def _handle_reject(self, appointment_id: int) -> None:
        """Prompts confirmation modal before rejecting an appointment."""
        ConfirmationModal(
            self,
            title="Reject Appointment",
            message=f"Are you sure you want to reject and cancel Appointment #{appointment_id}? This action cannot be undone.",
            confirm_text="Reject Appointment",
            cancel_text="Keep Pending",
            confirm_type="danger",
            on_confirm=lambda: self._execute_reject(appointment_id)
        )

    def _execute_reject(self, appointment_id: int) -> None:
        success, msg = self.appointment_service.update_status(appointment_id, STATUS_REJECTED)
        if success:
            self.show_toast(f"✕ Appointment #{appointment_id} marked as Rejected.", "warning")
            self.refresh_data()
        else:
            self.show_toast(msg, "error")

    def _export_to_csv(self) -> None:
        """Exports the current appointment list to a CSV file."""
        records = self.appointment_service.get_all_appointments()
        if not records:
            self.show_toast("No appointment records to export.", "warning")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile="medicare_appointments_export.csv"
        )
        if not file_path:
            return

        try:
            fieldnames = ["id", "patient_name", "contact_number", "doctor_name", "clinic_address", "app_date", "app_time_slot", "status", "booked_by", "created_at"]
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in records:
                    clean_row = {k: row.get(k, "") for k in fieldnames}
                    writer.writerow(clean_row)

            self.show_toast(f"Exported {len(records)} records to CSV successfully!", "success")
        except Exception as e:
            self.show_toast(f"Failed to export CSV: {e}", "error")

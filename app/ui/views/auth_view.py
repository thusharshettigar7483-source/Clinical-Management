"""
Authentication View for Medicare Specialist Portal.
Provides modern Login and Registration interfaces with real-time normalization,
password visibility toggle, and instant feedback.
"""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from app.config import APP_NAME, APP_SUBTITLE, COLORS
from app.services.auth_service import AuthService
from app.services.validation_service import ValidationService

class AuthView(ctk.CTkFrame):
    """
    Split-screen modern authentication view with Login and Registration panels.
    """
    def __init__(
        self,
        master,
        auth_service: AuthService,
        on_login_success: Callable[[Dict[str, Any]], None],
        show_toast: Callable[[str, str], None],
        **kwargs
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0B132B"), **kwargs)
        self.auth_service = auth_service
        self.on_login_success = on_login_success
        self.show_toast = show_toast

        self.current_mode = "login"  # "login" | "register"
        self.show_login_password = False
        self.show_reg_password = False
        self.show_reg_confirm_password = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()

    def _build_ui(self) -> None:
        # Centered container frame
        self.center_card = ctk.CTkFrame(
            self,
            corner_radius=20,
            border_width=1,
            fg_color=("#FFFFFF", "#1C2541"),
            border_color=("#E2E8F0", "#3A506B"),
            width=520
        )
        self.center_card.grid(row=0, column=0, padx=24, pady=24)
        self.center_card.grid_columnconfigure(0, weight=1)

        # Header branding section
        brand_frame = ctk.CTkFrame(self.center_card, fg_color="transparent")
        brand_frame.pack(fill="x", padx=36, pady=(36, 16))

        logo_icon = ctk.CTkLabel(
            brand_frame,
            text="🏥",
            font=ctk.CTkFont(size=36),
            width=64,
            height=64,
            corner_radius=16,
            fg_color=("#E0F2FE", "#0C4A6E")
        )
        logo_icon.pack(anchor="center", pady=(0, 12))

        title_lbl = ctk.CTkLabel(
            brand_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#0F172A", "#F8FAFC")
        )
        title_lbl.pack(anchor="center")

        sub_lbl = ctk.CTkLabel(
            brand_frame,
            text=APP_SUBTITLE,
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8")
        )
        sub_lbl.pack(anchor="center", pady=(2, 0))

        # Content area (swapped between login and registration)
        self.form_container = ctk.CTkFrame(self.center_card, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=36, pady=(0, 36))

        self._render_form()

    def _render_form(self) -> None:
        """Renders either login or registration form."""
        for widget in self.form_container.winfo_children():
            widget.destroy()

        if self.current_mode == "login":
            self._render_login_form()
        else:
            self._render_register_form()

    # ================= LOGIN FORM =================

    def _render_login_form(self) -> None:
        form = self.form_container

        heading_lbl = ctk.CTkLabel(
            form,
            text="Sign in to your account",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        heading_lbl.pack(fill="x", pady=(0, 16))

        # Username Field
        uname_lbl = ctk.CTkLabel(
            form,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        uname_lbl.pack(fill="x", pady=(0, 4))

        self.login_uname_entry = ctk.CTkEntry(
            form,
            placeholder_text="e.g. rahul_verma or admin",
            height=40,
            corner_radius=10,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.login_uname_entry.pack(fill="x", pady=(0, 4))
        self.login_uname_entry.bind("<KeyRelease>", self._on_login_uname_change)

        self.login_uname_hint = ctk.CTkLabel(
            form,
            text="* lowercase letters and underscores only (a-z, _)",
            font=ctk.CTkFont(size=10),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        self.login_uname_hint.pack(fill="x", pady=(0, 12))

        # Password Field
        pass_lbl = ctk.CTkLabel(
            form,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        pass_lbl.pack(fill="x", pady=(0, 4))

        pass_row = ctk.CTkFrame(form, fg_color="transparent")
        pass_row.pack(fill="x", pady=(0, 18))

        self.login_pass_entry = ctk.CTkEntry(
            pass_row,
            placeholder_text="Enter your password",
            show="•",
            height=40,
            corner_radius=10,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.login_pass_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.login_pass_entry.bind("<Return>", lambda event: self._handle_login_submit())

        self.login_toggle_pass_btn = ctk.CTkButton(
            pass_row,
            text="👁",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#F1F5F9", "#243256"),
            hover_color=("#E2E8F0", "#3A506B"),
            text_color=("#475569", "#CBD5E1"),
            font=ctk.CTkFont(size=14),
            command=self._toggle_login_password_visibility
        )
        self.login_toggle_pass_btn.pack(side="right")

        # Submit Login Button
        self.login_btn = ctk.CTkButton(
            form,
            text="Sign In ➜",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            command=self._handle_login_submit
        )
        self.login_btn.pack(fill="x", pady=(0, 16))

        # Demo Credentials Quick-Fill Chips
        demo_frame = ctk.CTkFrame(
            form,
            corner_radius=10,
            fg_color=("#F1F5F9", "#0E1838"),
            border_width=1,
            border_color=("#E2E8F0", "#3A506B")
        )
        demo_frame.pack(fill="x", pady=(0, 16), padx=2)

        demo_title = ctk.CTkLabel(
            demo_frame,
            text="⚡ Quick Demo Login:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#64748B", "#94A3B8")
        )
        demo_title.pack(anchor="w", padx=12, pady=(8, 4))

        demo_btns_row = ctk.CTkFrame(demo_frame, fg_color="transparent")
        demo_btns_row.pack(fill="x", padx=12, pady=(0, 8))

        admin_chip = ctk.CTkButton(
            demo_btns_row,
            text="👑 Admin (admin)",
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            fg_color=("#E0F2FE", "#0C4A6E"),
            text_color=("#0369A1", "#7DD3FC"),
            hover_color=("#BAE6FD", "#075985"),
            command=lambda: self._quick_fill("admin", "admin123")
        )
        admin_chip.pack(side="left", padx=(0, 6), expand=True, fill="x")

        patient_chip = ctk.CTkButton(
            demo_btns_row,
            text="👤 Patient (rahul_verma)",
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11),
            fg_color=("#D1FAE5", "#064E3B"),
            text_color=("#047857", "#6EE7B7"),
            hover_color=("#A7F3D0", "#065F46"),
            command=lambda: self._quick_fill("rahul_verma", "patient123")
        )
        patient_chip.pack(side="left", expand=True, fill="x")

        # Switch to Register Link
        switch_row = ctk.CTkFrame(form, fg_color="transparent")
        switch_row.pack(fill="x")

        switch_lbl = ctk.CTkLabel(
            switch_row,
            text="Don't have an account?",
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8")
        )
        switch_lbl.pack(side="left")

        switch_btn = ctk.CTkButton(
            switch_row,
            text="Create Patient Account",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            text_color=COLORS["primary_text"],
            hover_color=("#F1F5F9", "#243256"),
            width=150,
            command=self._switch_to_register
        )
        switch_btn.pack(side="right")

    # ================= REGISTRATION FORM =================

    def _render_register_form(self) -> None:
        form = self.form_container

        heading_lbl = ctk.CTkLabel(
            form,
            text="Register as New Patient",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            anchor="w"
        )
        heading_lbl.pack(fill="x", pady=(0, 16))

        # Username Field
        uname_lbl = ctk.CTkLabel(
            form,
            text="Choose Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        uname_lbl.pack(fill="x", pady=(0, 4))

        self.reg_uname_entry = ctk.CTkEntry(
            form,
            placeholder_text="e.g. anita_rao",
            height=40,
            corner_radius=10,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.reg_uname_entry.pack(fill="x", pady=(0, 4))
        self.reg_uname_entry.bind("<KeyRelease>", self._on_reg_uname_change)

        self.reg_uname_hint = ctk.CTkLabel(
            form,
            text="* lowercase letters and underscores only (a-z, _)",
            font=ctk.CTkFont(size=10),
            text_color=("#94A3B8", "#64748B"),
            anchor="w"
        )
        self.reg_uname_hint.pack(fill="x", pady=(0, 12))

        # Password Field
        pass_lbl = ctk.CTkLabel(
            form,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        pass_lbl.pack(fill="x", pady=(0, 4))

        pass_row = ctk.CTkFrame(form, fg_color="transparent")
        pass_row.pack(fill="x", pady=(0, 12))

        self.reg_pass_entry = ctk.CTkEntry(
            pass_row,
            placeholder_text="Minimum 4 characters",
            show="•",
            height=40,
            corner_radius=10,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.reg_pass_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.reg_toggle_pass_btn = ctk.CTkButton(
            pass_row,
            text="👁",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#F1F5F9", "#243256"),
            hover_color=("#E2E8F0", "#3A506B"),
            text_color=("#475569", "#CBD5E1"),
            font=ctk.CTkFont(size=14),
            command=self._toggle_reg_password_visibility
        )
        self.reg_toggle_pass_btn.pack(side="right")

        # Confirm Password Field
        confirm_lbl = ctk.CTkLabel(
            form,
            text="Confirm Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#334155", "#CBD5E1"),
            anchor="w"
        )
        confirm_lbl.pack(fill="x", pady=(0, 4))

        confirm_row = ctk.CTkFrame(form, fg_color="transparent")
        confirm_row.pack(fill="x", pady=(0, 18))

        self.reg_confirm_entry = ctk.CTkEntry(
            confirm_row,
            placeholder_text="Re-type your password",
            show="•",
            height=40,
            corner_radius=10,
            fg_color=("#F8FAFC", "#0E1838"),
            border_color=("#CBD5E1", "#3A506B"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(size=13)
        )
        self.reg_confirm_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.reg_confirm_entry.bind("<Return>", lambda event: self._handle_register_submit())

        self.reg_toggle_confirm_btn = ctk.CTkButton(
            confirm_row,
            text="👁",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("#F1F5F9", "#243256"),
            hover_color=("#E2E8F0", "#3A506B"),
            text_color=("#475569", "#CBD5E1"),
            font=ctk.CTkFont(size=14),
            command=self._toggle_reg_confirm_password_visibility
        )
        self.reg_toggle_confirm_btn.pack(side="right")

        # Submit Register Button
        self.register_btn = ctk.CTkButton(
            form,
            text="Create Account ➜",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="#FFFFFF",
            command=self._handle_register_submit
        )
        self.register_btn.pack(fill="x", pady=(0, 16))

        # Switch to Login Link
        switch_row = ctk.CTkFrame(form, fg_color="transparent")
        switch_row.pack(fill="x")

        switch_lbl = ctk.CTkLabel(
            switch_row,
            text="Already registered?",
            font=ctk.CTkFont(size=12),
            text_color=("#64748B", "#94A3B8")
        )
        switch_lbl.pack(side="left")

        switch_btn = ctk.CTkButton(
            switch_row,
            text="Sign In to Account",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            text_color=COLORS["primary_text"],
            hover_color=("#F1F5F9", "#243256"),
            width=150,
            command=self._switch_to_login
        )
        switch_btn.pack(side="right")

    # ================= LOGIC HANDLERS =================

    def _on_login_uname_change(self, event=None) -> None:
        """Instantly normalizes username (spaces to underscores, lowercase)."""
        raw_val = self.login_uname_entry.get()
        normalized = ValidationService.normalize_username(raw_val)
        if raw_val != normalized:
            cursor_pos = self.login_uname_entry.index(ctk.INSERT)
            self.login_uname_entry.delete(0, "end")
            self.login_uname_entry.insert(0, normalized)
            try:
                self.login_uname_entry.icursor(cursor_pos)
            except Exception:
                pass

    def _on_reg_uname_change(self, event=None) -> None:
        """Instantly normalizes username for registration."""
        raw_val = self.reg_uname_entry.get()
        normalized = ValidationService.normalize_username(raw_val)
        if raw_val != normalized:
            cursor_pos = self.reg_uname_entry.index(ctk.INSERT)
            self.reg_uname_entry.delete(0, "end")
            self.reg_uname_entry.insert(0, normalized)
            try:
                self.reg_uname_entry.icursor(cursor_pos)
            except Exception:
                pass

    def _toggle_login_password_visibility(self) -> None:
        self.show_login_password = not self.show_login_password
        if self.show_login_password:
            self.login_pass_entry.configure(show="")
            self.login_toggle_pass_btn.configure(text="🔒")
        else:
            self.login_pass_entry.configure(show="•")
            self.login_toggle_pass_btn.configure(text="👁")

    def _toggle_reg_password_visibility(self) -> None:
        self.show_reg_password = not self.show_reg_password
        if self.show_reg_password:
            self.reg_pass_entry.configure(show="")
            self.reg_toggle_pass_btn.configure(text="🔒")
        else:
            self.reg_pass_entry.configure(show="•")
            self.reg_toggle_pass_btn.configure(text="👁")

    def _toggle_reg_confirm_password_visibility(self) -> None:
        self.show_reg_confirm_password = not self.show_reg_confirm_password
        if self.show_reg_confirm_password:
            self.reg_confirm_entry.configure(show="")
            self.reg_toggle_confirm_btn.configure(text="🔒")
        else:
            self.reg_confirm_entry.configure(show="•")
            self.reg_toggle_confirm_btn.configure(text="👁")

    def _quick_fill(self, username: str, password: str) -> None:
        self.login_uname_entry.delete(0, "end")
        self.login_uname_entry.insert(0, username)
        self.login_pass_entry.delete(0, "end")
        self.login_pass_entry.insert(0, password)
        self.show_toast(f"Filled credentials for: {username}", "info")

    def _switch_to_register(self) -> None:
        self.current_mode = "register"
        self._render_form()

    def _switch_to_login(self) -> None:
        self.current_mode = "login"
        self._render_form()

    def _handle_login_submit(self) -> None:
        uname = self.login_uname_entry.get()
        pwd = self.login_pass_entry.get()

        success, user_dict, msg = self.auth_service.login(uname, pwd)
        if success and user_dict:
            self.show_toast(msg, "success")
            self.on_login_success(user_dict)
        else:
            self.show_toast(msg, "error")

    def _handle_register_submit(self) -> None:
        uname = self.reg_uname_entry.get()
        pwd = self.reg_pass_entry.get()
        confirm_pwd = self.reg_confirm_entry.get()

        success, msg = self.auth_service.register(uname, pwd, confirm_pwd, role="patient")
        if success:
            self.show_toast(msg, "success")
            # Auto switch to login view and prefill username
            self.current_mode = "login"
            self._render_form()
            self.login_uname_entry.delete(0, "end")
            self.login_uname_entry.insert(0, uname)
            self.login_pass_entry.focus()
        else:
            self.show_toast(msg, "error")

"""
Main Application Window for Medicare Specialist Portal.
Orchestrates screen routing, session state, theme management, and global toast feedback.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any
from app.config import (
    APP_NAME,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT
)
from app.database.db_manager import DatabaseManager
from app.database.seed_data import seed_database
from app.services.auth_service import AuthService
from app.services.appointment_service import AppointmentService
from app.ui.components.toast import ToastNotification
from app.ui.views.auth_view import AuthView
from app.ui.views.patient_view import PatientView
from app.ui.views.history_view import HistoryView
from app.ui.views.admin_view import AdminView

class MainWindow(ctk.CTk):
    """
    Main application frame managing screen switches and global services.
    """
    def __init__(self):
        super().__init__()

        # Configure Window Properties
        self.title(f"{APP_NAME} — Specialist Healthcare Network")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Center window on screen
        self._center_window(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Appearance mode and theme
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        # Initialize Services & Seed Database
        self.db = DatabaseManager.get_instance()
        seed_database(self.db)

        self.auth_service = AuthService(self.db)
        self.appointment_service = AppointmentService(self.db)

        # Active Session
        self.current_user: Optional[Dict[str, Any]] = None
        self.current_view: Optional[ctk.CTkFrame] = None

        # Container for screens
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Floating Toast Notification System
        self.toast = ToastNotification(self)

        # Start at Authentication Screen
        self.show_auth_screen()

    def _center_window(self, width: int, height: int) -> None:
        """Positions window at the center of the primary display."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_toast(self, message: str, toast_type: str = "info", duration_ms: int = 3500) -> None:
        """Global toast notification trigger."""
        self.toast.show(message, toast_type=toast_type, duration_ms=duration_ms)

    def _clear_current_view(self) -> None:
        """Destroys current view before routing to a new one."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

    # ================= SCREEN ROUTING =================

    def show_auth_screen(self) -> None:
        """Renders Login & Registration screen."""
        self._clear_current_view()
        self.current_user = None

        self.current_view = AuthView(
            master=self.container,
            auth_service=self.auth_service,
            on_login_success=self._on_login_success,
            show_toast=self.show_toast
        )
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def _on_login_success(self, user_info: Dict[str, Any]) -> None:
        """Handles post-login routing according to user role."""
        self.current_user = user_info
        role = user_info.get("role", "patient")

        if role == "admin":
            self.show_admin_dashboard()
        else:
            self.show_patient_dashboard()

    def show_patient_dashboard(self) -> None:
        """Renders Patient Appointment Booking screen."""
        if not self.current_user:
            self.show_auth_screen()
            return

        self._clear_current_view()
        self.current_view = PatientView(
            master=self.container,
            user_info=self.current_user,
            appointment_service=self.appointment_service,
            on_view_history=self.show_patient_history,
            on_logout=self.logout,
            show_toast=self.show_toast
        )
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def show_patient_history(self) -> None:
        """Renders Patient Appointment Records / History screen."""
        if not self.current_user:
            self.show_auth_screen()
            return

        self._clear_current_view()
        self.current_view = HistoryView(
            master=self.container,
            user_info=self.current_user,
            appointment_service=self.appointment_service,
            on_back_to_booking=self.show_patient_dashboard,
            on_logout=self.logout,
            show_toast=self.show_toast
        )
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def show_admin_dashboard(self) -> None:
        """Renders Admin Command Center."""
        if not self.current_user:
            self.show_auth_screen()
            return

        self._clear_current_view()
        self.current_view = AdminView(
            master=self.container,
            user_info=self.current_user,
            appointment_service=self.appointment_service,
            on_logout=self.logout,
            show_toast=self.show_toast
        )
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def logout(self) -> None:
        """Clears session and routes back to login screen."""
        user_name = self.current_user.get("username", "") if self.current_user else ""
        self.current_user = None
        self.show_auth_screen()
        if user_name:
            self.show_toast(f"Successfully logged out. See you soon, {user_name}!", "info")

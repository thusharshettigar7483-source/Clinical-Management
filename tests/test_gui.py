"""
GUI Integration Test for Medicare Specialist Portal.
Tests window instantiation, view transitions, modal/toast creation, and clean teardown.
"""

import unittest
import os
import tempfile
import customtkinter as ctk
from app.database.db_manager import DatabaseManager
from app.ui.main_window import MainWindow
from app.ui.components.date_picker import CalendarDatePickerDialog
from app.ui.components.modal import ConfirmationModal
from app.config import STATUS_PENDING

class TestGUIIntegration(unittest.TestCase):
    def setUp(self):
        # Disable Tk mainloop blocking
        self.app = MainWindow()
        self.app.withdraw()  # Keep window hidden during test execution

    def tearDown(self):
        try:
            self.app.destroy()
        except Exception:
            pass

    def test_main_window_startup(self):
        self.assertIsNotNone(self.app)
        self.assertIsNotNone(self.app.current_view)
        # Should start with AuthView
        self.assertEqual(self.app.current_view.__class__.__name__, "AuthView")

    def test_routing_to_patient_dashboard_and_history(self):
        sample_patient = {"id": 1, "username": "rahul_verma", "role": "patient"}
        self.app._on_login_success(sample_patient)
        self.app.update()

        # Check that PatientView is active
        self.assertEqual(self.app.current_view.__class__.__name__, "PatientView")

        # Navigate to History
        self.app.show_patient_history()
        self.app.update()
        self.assertEqual(self.app.current_view.__class__.__name__, "HistoryView")

        # Navigate back to Booking
        self.app.show_patient_dashboard()
        self.app.update()
        self.assertEqual(self.app.current_view.__class__.__name__, "PatientView")

    def test_routing_to_admin_dashboard(self):
        admin_user = {"id": 1, "username": "admin", "role": "admin"}
        self.app._on_login_success(admin_user)
        self.app.update()

        # Check that AdminView is active
        self.assertEqual(self.app.current_view.__class__.__name__, "AdminView")

    def test_toast_notification(self):
        self.app.show_toast("Test notification message", "success", duration_ms=100)
        self.app.update()
        self.assertTrue(self.app.toast._is_showing)
        self.app.toast.dismiss()
        self.app.update()
        self.assertFalse(self.app.toast._is_showing)

    def test_date_picker_dialog(self):
        selected_dates = []
        def on_selected(d):
            selected_dates.append(d)

        dlg = CalendarDatePickerDialog(self.app, on_date_selected=on_selected)
        self.app.update()
        self.assertIsNotNone(dlg)
        dlg._select_date(dlg.min_date)
        self.app.update()
        self.assertEqual(len(selected_dates), 1)

    def test_confirmation_modal(self):
        confirmed = []
        def on_confirmed():
            confirmed.append(True)

        modal = ConfirmationModal(
            self.app,
            title="Test Confirmation",
            message="Are you sure?",
            on_confirm=on_confirmed
        )
        self.app.update()
        self.assertIsNotNone(modal)
        modal._handle_confirm()
        self.app.update()
        self.assertEqual(confirmed, [True])

if __name__ == "__main__":
    unittest.main()

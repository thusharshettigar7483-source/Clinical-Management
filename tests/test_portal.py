"""
Comprehensive Automated Test Suite for Medicare Specialist Portal.
Validates Database, Authentication, Validations, and Appointment Services.
"""

import unittest
import os
import tempfile
import datetime
from app.database.db_manager import DatabaseManager
from app.database.seed_data import seed_database
from app.services.auth_service import AuthService
from app.services.appointment_service import AppointmentService
from app.services.validation_service import ValidationService
from app.config import (
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_REJECTED,
    DOCTOR_SCHEDULE_MATRIX,
    TIME_SLOTS
)

class TestMedicareSpecialistPortal(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file for isolated testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = DatabaseManager(self.temp_db.name)
        self.auth_service = AuthService(self.db)
        self.appointment_service = AppointmentService(self.db)

    def tearDown(self):
        # Clean up temporary database
        try:
            os.remove(self.temp_db.name)
        except Exception:
            pass

    # ================= 1. AUTHENTICATION & PASSWORD HASHING =================

    def test_password_hashing_and_verification(self):
        pwd = "SecretPassword123"
        pwd_hash = self.auth_service.hash_password(pwd)
        
        self.assertIn("$", pwd_hash)
        self.assertTrue(self.auth_service.verify_password(pwd, pwd_hash))
        self.assertFalse(self.auth_service.verify_password("WrongPassword", pwd_hash))

    def test_user_registration_and_login(self):
        # Register new patient
        ok, msg = self.auth_service.register("dr_anita", "pass123", "pass123", role="patient")
        self.assertTrue(ok, f"Registration failed: {msg}")

        # Attempt duplicate registration
        ok_dup, msg_dup = self.auth_service.register("dr_anita", "pass123", "pass123")
        self.assertFalse(ok_dup)
        self.assertIn("already taken", msg_dup)

        # Login with correct password
        success, user, login_msg = self.auth_service.login("dr_anita", "pass123")
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "dr_anita")
        self.assertEqual(user["role"], "patient")

        # Login with wrong password
        fail_success, _, fail_msg = self.auth_service.login("dr_anita", "wrongpass")
        self.assertFalse(fail_success)

    # ================= 2. INPUT VALIDATIONS =================

    def test_username_normalization_and_validation(self):
        self.assertEqual(ValidationService.normalize_username("  John Doe  "), "john_doe")
        self.assertEqual(ValidationService.normalize_username("Alice"), "alice")

        # Valid usernames
        val1, _ = ValidationService.validate_username("rohit_kumar")
        self.assertTrue(val1)
        val2, _ = ValidationService.validate_username("admin")
        self.assertTrue(val2)

        # Invalid usernames (contains numbers, special symbols, uppercase before norm)
        inv1, _ = ValidationService.validate_username("user123")
        self.assertFalse(inv1)
        inv2, _ = ValidationService.validate_username("user@name")
        self.assertFalse(inv2)

    def test_patient_name_validation(self):
        # Valid names
        val1, _ = ValidationService.validate_patient_name("Rahul Verma")
        self.assertTrue(val1)
        val2, _ = ValidationService.validate_patient_name("Dr John Doe")
        self.assertTrue(val2)

        # Invalid names (contains digits or symbols)
        inv1, _ = ValidationService.validate_patient_name("Rahul123")
        self.assertFalse(inv1)
        inv2, _ = ValidationService.validate_patient_name("")
        self.assertFalse(inv2)

    def test_contact_number_validation_and_formatting(self):
        formatted = ValidationService.format_contact_number("9845123456")
        self.assertEqual(formatted, "+91 9845123456")

        val_ok, _ = ValidationService.validate_contact_number("+91 9845123456")
        self.assertTrue(val_ok)

        # Invalid contact numbers
        inv1, _ = ValidationService.validate_contact_number("9845123456") # Missing prefix
        self.assertFalse(inv1)
        inv2, _ = ValidationService.validate_contact_number("+91 12345") # Incomplete digits
        self.assertFalse(inv2)

    def test_appointment_date_future_restriction(self):
        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")
        tomorrow_str = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        next_month_str = (today + datetime.timedelta(days=30)).strftime("%Y-%m-%d")

        # Yesterday and today must be rejected
        inv_past, _ = ValidationService.validate_appointment_date(yesterday)
        self.assertFalse(inv_past)
        inv_today, _ = ValidationService.validate_appointment_date(today_str)
        self.assertFalse(inv_today)

        # Tomorrow and future dates must be accepted
        val_tmrw, _ = ValidationService.validate_appointment_date(tomorrow_str)
        self.assertTrue(val_tmrw)
        val_future, _ = ValidationService.validate_appointment_date(next_month_str)
        self.assertTrue(val_future)

    # ================= 3. DOCTOR & SCHEDULE MATRIX =================

    def test_doctor_schedule_matrix_resolution(self):
        # Dr. Sharma (Cardio)
        sharma_11 = AppointmentService.get_clinic_info("Dr. Sharma (Cardio)", "11 AM - 1 PM")
        self.assertEqual(sharma_11["branch"], "Surathkal Branch")
        sharma_3 = AppointmentService.get_clinic_info("Dr. Sharma (Cardio)", "3 PM - 5 PM")
        self.assertEqual(sharma_3["branch"], "Pumpwell Branch")

        # Dr. Gupta (Neuro)
        gupta_11 = AppointmentService.get_clinic_info("Dr. Gupta (Neuro)", "11 AM - 1 PM")
        self.assertEqual(gupta_11["branch"], "Bondel Branch")
        gupta_3 = AppointmentService.get_clinic_info("Dr. Gupta (Neuro)", "3 PM - 5 PM")
        self.assertEqual(gupta_3["branch"], "Kulur Branch")

        # Dr. Satwik Rai (Physio)
        rai_11 = AppointmentService.get_clinic_info("Dr. Satwik Rai (Physio)", "11 AM - 1 PM")
        self.assertEqual(rai_11["branch"], "Ladyhill Branch")
        rai_3 = AppointmentService.get_clinic_info("Dr. Satwik Rai (Physio)", "3 PM - 5 PM")
        self.assertEqual(rai_3["branch"], "PVS Branch")

        # Dr. Ashika Shetty (ENT)
        shetty_11 = AppointmentService.get_clinic_info("Dr. Ashika Shetty (ENT)", "11 AM - 1 PM")
        self.assertEqual(shetty_11["branch"], "Kodialbail Branch")
        shetty_3 = AppointmentService.get_clinic_info("Dr. Ashika Shetty (ENT)", "3 PM - 5 PM")
        self.assertEqual(shetty_3["branch"], "Sulthan Bathery Branch")

        # Dr. Nikhil Poojary (Ortho)
        poojary_11 = AppointmentService.get_clinic_info("Dr. Nikhil Poojary (Ortho)", "11 AM - 1 PM")
        self.assertEqual(poojary_11["branch"], "Ullal Branch")
        poojary_3 = AppointmentService.get_clinic_info("Dr. Nikhil Poojary (Ortho)", "3 PM - 5 PM")
        self.assertEqual(poojary_3["branch"], "Yekkur Branch")

    # ================= 4. APPOINTMENT BOOKING & STATUS WORKFLOW =================

    def test_appointment_booking_workflow(self):
        # Register patient
        self.auth_service.register("patient_user", "patient123", "patient123")

        tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # Book appointment
        ok, app_id, msg = self.appointment_service.book_appointment(
            patient_name="Rahul Verma",
            contact_number="+91 9845123456",
            doctor_name="Dr. Sharma (Cardio)",
            time_slot="11 AM - 1 PM",
            app_date=tomorrow_str,
            booked_by="patient_user"
        )
        self.assertTrue(ok)
        self.assertIsNotNone(app_id)

        # Verify initial status is Pending
        app_record = self.db.get_appointment_by_id(app_id)
        self.assertEqual(app_record["status"], STATUS_PENDING)
        self.assertIn("Surathkal", app_record["clinic_address"])

        # Admin Confirms Appointment
        ok_confirm, msg_conf = self.appointment_service.update_status(app_id, STATUS_CONFIRMED)
        self.assertTrue(ok_confirm)
        updated_app = self.db.get_appointment_by_id(app_id)
        self.assertEqual(updated_app["status"], STATUS_CONFIRMED)

        # Attempting to change an already confirmed appointment should fail
        ok_re_reject, msg_re = self.appointment_service.update_status(app_id, STATUS_REJECTED)
        self.assertFalse(ok_re_reject)
        self.assertIn("already 'Confirmed'", msg_re)

    def test_seed_database(self):
        seed_database(self.db)
        
        # Verify default admin account exists
        admin = self.db.get_user_by_username("admin")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")
        self.assertTrue(self.auth_service.verify_password("admin123", admin["password"]))

        # Verify seeded sample appointments exist
        all_apps = self.db.get_all_appointments()
        self.assertGreaterEqual(len(all_apps), 5)

        # Verify stats calculation
        stats = self.appointment_service.get_dashboard_stats()
        self.assertGreater(stats["total"], 0)
        self.assertGreaterEqual(stats["pending"], 1)
        self.assertGreaterEqual(stats["confirmed"], 1)

if __name__ == "__main__":
    unittest.main()

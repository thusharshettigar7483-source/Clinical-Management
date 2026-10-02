"""
Appointment Service for Medicare Specialist Portal.
Handles appointment scheduling, clinic location resolution, status management, and reporting.
"""

from typing import List, Dict, Any, Optional, Tuple
from app.database.db_manager import DatabaseManager
from app.config import (
    DOCTOR_SCHEDULE_MATRIX,
    TIME_SLOTS,
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_REJECTED
)
from app.services.validation_service import ValidationService

class AppointmentService:
    """Business logic for appointments."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager.get_instance()

    @staticmethod
    def get_clinic_info(doctor_name: str, time_slot: str) -> Optional[Dict[str, str]]:
        """
        Looks up clinic address and branch metadata for a given doctor and time slot.
        """
        if doctor_name not in DOCTOR_SCHEDULE_MATRIX:
            return None
        doc_data = DOCTOR_SCHEDULE_MATRIX[doctor_name]
        slots = doc_data.get("slots", {})
        if time_slot not in slots:
            return None
        return slots[time_slot]

    @staticmethod
    def get_clinic_address_string(doctor_name: str, time_slot: str) -> str:
        """
        Returns full address string for saving in the database.
        """
        info = AppointmentService.get_clinic_info(doctor_name, time_slot)
        if not info:
            return "Address unavailable"
        return f"{info['branch']}, {info['address']} ({info['room']})"

    def book_appointment(
        self,
        patient_name: str,
        contact_number: str,
        doctor_name: str,
        time_slot: str,
        app_date: str,
        booked_by: str
    ) -> Tuple[bool, Optional[int], str]:
        """
        Validates all fields and inserts a new appointment.
        Returns: (success: bool, appointment_id: Optional[int], message: str)
        """
        # Validate patient name
        valid_name, name_err = ValidationService.validate_patient_name(patient_name)
        if not valid_name:
            return False, None, name_err

        # Validate contact number
        valid_contact, contact_err = ValidationService.validate_contact_number(contact_number)
        if not valid_contact:
            return False, None, contact_err

        # Validate doctor and slot
        valid_doc_slot, doc_slot_err = ValidationService.validate_doctor_and_slot(doctor_name, time_slot)
        if not valid_doc_slot:
            return False, None, doc_slot_err

        # Validate appointment date
        valid_date, date_err = ValidationService.validate_appointment_date(app_date)
        if not valid_date:
            return False, None, date_err

        # Get full clinic address string
        clinic_address = self.get_clinic_address_string(doctor_name, time_slot)

        # Insert appointment
        app_id = self.db.create_appointment(
            patient_name=patient_name.strip(),
            contact_number=contact_number.strip(),
            doctor_name=doctor_name.strip(),
            clinic_address=clinic_address,
            app_date=app_date.strip(),
            app_time_slot=time_slot.strip(),
            booked_by=booked_by.lower().strip(),
            status=STATUS_PENDING
        )

        if app_id:
            return True, app_id, f"Appointment successfully scheduled for {patient_name.strip()} on {app_date} ({time_slot})!"
        else:
            return False, None, "Database error: Failed to record appointment. Please try again."

    def get_patient_appointments(self, username: str, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all appointments booked by a patient."""
        return self.db.get_appointments_by_user(username, search_query)

    def get_all_appointments(
        self,
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None,
        doctor_filter: Optional[str] = None,
        date_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all appointments for admin view with filtering."""
        return self.db.get_all_appointments(
            search_query=search_query,
            status_filter=status_filter,
            doctor_filter=doctor_filter,
            date_filter=date_filter
        )

    def update_status(self, appointment_id: int, new_status: str) -> Tuple[bool, str]:
        """
        Updates status to Confirmed or Rejected.
        Enforces rule that only Pending appointments can be modified.
        """
        app = self.db.get_appointment_by_id(appointment_id)
        if not app:
            return False, f"Appointment #{appointment_id} not found."

        if app["status"] != STATUS_PENDING:
            return False, f"Appointment #{appointment_id} is already '{app['status']}' and cannot be altered."

        success = self.db.update_appointment_status(appointment_id, new_status)
        if success:
            return True, f"Appointment #{appointment_id} marked as '{new_status}'."
        else:
            return False, f"Failed to update Appointment #{appointment_id}."

    def get_dashboard_stats(self) -> Dict[str, int]:
        """Fetch summary metrics for admin command center."""
        return self.db.get_appointment_stats()

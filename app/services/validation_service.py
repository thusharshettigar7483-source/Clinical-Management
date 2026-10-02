"""
Validation Service for Medicare Specialist Portal.
Enforces strict regex patterns and business validation rules.
"""

import re
from datetime import datetime, date, timedelta
from typing import Tuple
from app.config import DOCTOR_SCHEDULE_MATRIX, TIME_SLOTS

class ValidationService:
    """Provides validation methods for authentication and booking inputs."""

    @staticmethod
    def normalize_username(raw_username: str) -> str:
        """
        Normalizes username by converting spaces to underscores and lowercasing.
        """
        if not raw_username:
            return ""
        # Replace consecutive spaces with single underscore, trim, and lower
        cleaned = re.sub(r'\s+', '_', raw_username.strip())
        return cleaned.lower()

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validates that username matches ^[a-z_]+$ and has reasonable length.
        """
        normalized = ValidationService.normalize_username(username)
        if not normalized:
            return False, "Username cannot be empty."
        
        if len(normalized) < 3:
            return False, "Username must be at least 3 characters long."
        
        if len(normalized) > 30:
            return False, "Username must be at most 30 characters long."

        if not re.match(r"^[a-z_]+$", normalized):
            return False, "Username can only contain lowercase letters and underscores (a-z, _)."

        return True, ""

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validates password length and presence.
        """
        if not password:
            return False, "Password cannot be empty."
        if len(password) < 4:
            return False, "Password must be at least 4 characters long."
        return True, ""

    @staticmethod
    def validate_patient_name(name: str) -> Tuple[bool, str]:
        """
        Validates that patient name contains only letters and spaces (^[a-zA-Z ]+$).
        """
        cleaned = name.strip() if name else ""
        if not cleaned:
            return False, "Patient full name is required."
        
        if len(cleaned) < 2:
            return False, "Patient name must be at least 2 characters long."
            
        if not re.match(r"^[a-zA-Z\s]+$", cleaned):
            return False, "Patient name must contain only letters and spaces (no numbers/symbols)."

        return True, ""

    @staticmethod
    def format_contact_number(raw_phone: str) -> str:
        """
        Cleans and formats a contact number with '+91 ' prefix.
        """
        if not raw_phone:
            return "+91 "
        raw_phone = raw_phone.strip()
        if raw_phone.startswith("+91 "):
            digits_only = re.sub(r"\D", "", raw_phone[4:])
            return f"+91 {digits_only[:10]}"
        elif raw_phone.startswith("+91"):
            digits_only = re.sub(r"\D", "", raw_phone[3:])
            return f"+91 {digits_only[:10]}"
        else:
            digits_only = re.sub(r"\D", "", raw_phone)
            return f"+91 {digits_only[:10]}"

    @staticmethod
    def validate_contact_number(contact: str) -> Tuple[bool, str]:
        r"""
        Validates contact number strictly matches ^\+91 \d{10}$.
        """
        cleaned = contact.strip() if contact else ""
        if not cleaned:
            return False, "Contact number is required."

        if not re.match(r"^\+91 \d{10}$", cleaned):
            return False, "Contact number must be in the format: +91 XXXXXXXXXX (10 digits)."

        return True, ""

    @staticmethod
    def validate_appointment_date(date_str: str) -> Tuple[bool, str]:
        """
        Validates appointment date is formatted YYYY-MM-DD and strictly in future (tomorrow or later).
        """
        if not date_str or not date_str.strip():
            return False, "Appointment date is required."

        try:
            parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Expected YYYY-MM-DD."

        today = date.today()
        tomorrow = today + timedelta(days=1)

        if parsed_date < tomorrow:
            return False, f"Appointment date must be tomorrow ({tomorrow.strftime('%Y-%m-%d')}) or later."

        # Maximum booking horizon (e.g. within next 90 days)
        max_horizon = today + timedelta(days=90)
        if parsed_date > max_horizon:
            return False, f"Appointments can only be booked up to 90 days in advance (until {max_horizon.strftime('%Y-%m-%d')})."

        return True, ""

    @staticmethod
    def validate_doctor_and_slot(doctor_name: str, time_slot: str) -> Tuple[bool, str]:
        """
        Validates doctor and time slot selection against schedule matrix.
        """
        if doctor_name not in DOCTOR_SCHEDULE_MATRIX:
            return False, "Please select a valid specialist doctor."

        if time_slot not in TIME_SLOTS:
            return False, "Please select a valid time slot."

        doctor_info = DOCTOR_SCHEDULE_MATRIX[doctor_name]
        if time_slot not in doctor_info["slots"]:
            return False, f"{doctor_name} is not available during {time_slot}."

        return True, ""

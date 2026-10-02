"""
Seed data script to initialize default admin account and sample clinic records.
"""

from datetime import date, timedelta
from app.database.db_manager import DatabaseManager
from app.services.auth_service import AuthService
from app.services.appointment_service import AppointmentService
from app.config import (
    STATUS_PENDING,
    STATUS_CONFIRMED,
    STATUS_REJECTED,
    DOCTOR_LIST,
    TIME_SLOTS
)

def seed_database(db: DatabaseManager) -> None:
    """Seeds the database with admin and sample data if not already populated."""
    auth_service = AuthService(db)
    app_service = AppointmentService(db)

    # 1. Ensure Default Admin Account Exists
    admin_user = db.get_user_by_username("admin")
    if not admin_user:
        admin_pass_hash = auth_service.hash_password("admin123")
        db.create_user(username="admin", password_hash=admin_pass_hash, role="admin")
        print("[Seed] Created default admin account: admin / admin123")

    # 2. Ensure Sample Patient Accounts Exist
    sample_patients = [
        ("rahul_verma", "patient123"),
        ("priya_shetty", "patient123"),
        ("vikram_nayak", "patient123"),
    ]
    for uname, pwd in sample_patients:
        if not db.get_user_by_username(uname):
            pwd_hash = auth_service.hash_password(pwd)
            db.create_user(username=uname, password_hash=pwd_hash, role="patient")
            print(f"[Seed] Created sample patient account: {uname} / {pwd}")

    # 3. Populate Initial Sample Appointments if table is empty
    all_apps = db.get_all_appointments()
    if len(all_apps) == 0:
        today = date.today()
        d_tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        d_plus_2 = (today + timedelta(days=2)).strftime("%Y-%m-%d")
        d_plus_4 = (today + timedelta(days=4)).strftime("%Y-%m-%d")
        d_plus_5 = (today + timedelta(days=5)).strftime("%Y-%m-%d")

        sample_appointments = [
            {
                "patient_name": "Rahul Verma",
                "contact_number": "+91 9845123456",
                "doctor_name": "Dr. Sharma (Cardio)",
                "time_slot": "11 AM - 1 PM",
                "app_date": d_tomorrow,
                "booked_by": "rahul_verma",
                "status": STATUS_PENDING
            },
            {
                "patient_name": "Priya Shetty",
                "contact_number": "+91 9876543210",
                "doctor_name": "Dr. Ashika Shetty (ENT)",
                "time_slot": "3 PM - 5 PM",
                "app_date": d_tomorrow,
                "booked_by": "priya_shetty",
                "status": STATUS_CONFIRMED
            },
            {
                "patient_name": "Vikram Nayak",
                "contact_number": "+91 9448112233",
                "doctor_name": "Dr. Gupta (Neuro)",
                "time_slot": "11 AM - 1 PM",
                "app_date": d_plus_2,
                "booked_by": "vikram_nayak",
                "status": STATUS_PENDING
            },
            {
                "patient_name": "Ananya Rao",
                "contact_number": "+91 9880192837",
                "doctor_name": "Dr. Nikhil Poojary (Ortho)",
                "time_slot": "3 PM - 5 PM",
                "app_date": d_plus_4,
                "booked_by": "rahul_verma",
                "status": STATUS_CONFIRMED
            },
            {
                "patient_name": "Suresh Kamath",
                "contact_number": "+91 9741002288",
                "doctor_name": "Dr. Satwik Rai (Physio)",
                "time_slot": "11 AM - 1 PM",
                "app_date": d_plus_5,
                "booked_by": "priya_shetty",
                "status": STATUS_REJECTED
            },
        ]

        for item in sample_appointments:
            addr = app_service.get_clinic_address_string(item["doctor_name"], item["time_slot"])
            db.create_appointment(
                patient_name=item["patient_name"],
                contact_number=item["contact_number"],
                doctor_name=item["doctor_name"],
                clinic_address=addr,
                app_date=item["app_date"],
                app_time_slot=item["time_slot"],
                booked_by=item["booked_by"],
                status=item["status"]
            )
        print("[Seed] Seeded 5 initial sample appointments.")

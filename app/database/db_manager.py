"""
Database Manager for Medicare Specialist Portal.
Handles SQLite connection, schema creation, migrations, and CRUD operations.
"""

import sqlite3
import os
import threading
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, Generator
from app.config import DB_NAME, STATUS_PENDING, STATUS_CONFIRMED, STATUS_REJECTED

class DatabaseManager:
    """Manages SQLite database connections and queries with automatic resource cleanup."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.db_path = os.path.abspath(DB_NAME)
        else:
            self.db_path = db_path
        self._initialize_database()

    @classmethod
    def get_instance(cls, db_path: Optional[str] = None) -> "DatabaseManager":
        """Singleton accessor for thread-safe database operations."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(db_path)
            return cls._instance

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Yields a managed SQLite connection and ensures it is properly closed."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_database(self) -> None:
        """Create tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'patient')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Appointments Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_number TEXT NOT NULL,
                    patient_name TEXT NOT NULL,
                    doctor_name TEXT NOT NULL,
                    clinic_address TEXT NOT NULL,
                    app_date TEXT NOT NULL,
                    app_time_slot TEXT NOT NULL,
                    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Confirmed', 'Rejected')),
                    booked_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (booked_by) REFERENCES users (username) ON DELETE CASCADE
                );
            """)

            # Create Indexes for fast querying
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_appointments_booked_by ON appointments (booked_by);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments (status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments (app_date);")

            conn.commit()

    # ================= USER OPERATIONS =================

    def create_user(self, username: str, password_hash: str, role: str = "patient") -> bool:
        """
        Inserts a new user record. Returns True on success, False if username exists.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username.lower().strip(), password_hash, role)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"[DB Error] create_user: {e}")
            return False

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch user record by username."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password, role, created_at FROM users WHERE username = ?",
                    (username.lower().strip(),)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"[DB Error] get_user_by_username: {e}")
            return None

    def user_exists(self, username: str) -> bool:
        """Check if a username already exists."""
        return self.get_user_by_username(username) is not None

    # ================= APPOINTMENT OPERATIONS =================

    def create_appointment(
        self,
        patient_name: str,
        contact_number: str,
        doctor_name: str,
        clinic_address: str,
        app_date: str,
        app_time_slot: str,
        booked_by: str,
        status: str = STATUS_PENDING
    ) -> Optional[int]:
        """
        Create a new appointment. Returns the inserted appointment ID on success, None on error.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO appointments (
                        patient_name, contact_number, doctor_name, clinic_address,
                        app_date, app_time_slot, status, booked_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_name.strip(),
                    contact_number.strip(),
                    doctor_name.strip(),
                    clinic_address.strip(),
                    app_date.strip(),
                    app_time_slot.strip(),
                    status,
                    booked_by.lower().strip()
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"[DB Error] create_appointment: {e}")
            return None

    def get_appointments_by_user(self, username: str, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all appointments booked by a specific user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM appointments WHERE booked_by = ?"
                params = [username.lower().strip()]

                if search_query:
                    search_term = f"%{search_query.strip()}%"
                    query += " AND (doctor_name LIKE ? OR patient_name LIKE ? OR clinic_address LIKE ? OR app_date LIKE ?)"
                    params.extend([search_term, search_term, search_term, search_term])

                query += " ORDER BY app_date DESC, id DESC"
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB Error] get_appointments_by_user: {e}")
            return []

    def get_all_appointments(
        self,
        search_query: Optional[str] = None,
        status_filter: Optional[str] = None,
        doctor_filter: Optional[str] = None,
        date_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all appointments with flexible filtering and searching."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM appointments WHERE 1=1"
                params: List[Any] = []

                if status_filter and status_filter != "All":
                    query += " AND status = ?"
                    params.append(status_filter)

                if doctor_filter and doctor_filter != "All Doctors":
                    query += " AND doctor_name = ?"
                    params.append(doctor_filter)

                if date_filter and date_filter.strip():
                    query += " AND app_date = ?"
                    params.append(date_filter.strip())

                if search_query and search_query.strip():
                    q = f"%{search_query.strip()}%"
                    query += """ AND (
                        patient_name LIKE ? OR
                        contact_number LIKE ? OR
                        doctor_name LIKE ? OR
                        clinic_address LIKE ? OR
                        booked_by LIKE ? OR
                        id LIKE ?
                    )"""
                    params.extend([q, q, q, q, q, q])

                query += " ORDER BY CASE WHEN status = 'Pending' THEN 1 WHEN status = 'Confirmed' THEN 2 ELSE 3 END, app_date ASC, id DESC"
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"[DB Error] get_all_appointments: {e}")
            return []

    def get_appointment_by_id(self, appointment_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single appointment by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"[DB Error] get_appointment_by_id: {e}")
            return None

    def update_appointment_status(self, appointment_id: int, new_status: str) -> bool:
        """
        Update status to 'Confirmed' or 'Rejected'. Returns True on success.
        """
        if new_status not in (STATUS_CONFIRMED, STATUS_REJECTED, STATUS_PENDING):
            return False
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE appointments SET status = ? WHERE id = ?",
                    (new_status, appointment_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB Error] update_appointment_status: {e}")
            return False

    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment by ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[DB Error] delete_appointment: {e}")
            return False

    def get_appointment_stats(self) -> Dict[str, int]:
        """Calculate counts for summary stats on admin dashboard."""
        stats = {
            "total": 0,
            "pending": 0,
            "confirmed": 0,
            "rejected": 0,
            "today": 0
        }
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status, COUNT(*) as cnt FROM appointments GROUP BY status")
                for row in cursor.fetchall():
                    s = row["status"]
                    cnt = row["cnt"]
                    stats["total"] += cnt
                    if s == STATUS_PENDING:
                        stats["pending"] = cnt
                    elif s == STATUS_CONFIRMED:
                        stats["confirmed"] = cnt
                    elif s == STATUS_REJECTED:
                        stats["rejected"] = cnt

                cursor.execute("SELECT COUNT(*) as cnt FROM appointments WHERE app_date = date('now')")
                today_row = cursor.fetchone()
                if today_row:
                    stats["today"] = today_row["cnt"]

        except Exception as e:
            print(f"[DB Error] get_appointment_stats: {e}")
        return stats

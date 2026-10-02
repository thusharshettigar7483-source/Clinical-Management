"""
Authentication Service for Medicare Specialist Portal.
Handles password hashing, user registration, and login validation.
"""

import hashlib
import os
import hmac
from typing import Optional, Dict, Any, Tuple
from app.database.db_manager import DatabaseManager
from app.services.validation_service import ValidationService

class AuthService:
    """Provides user authentication and registration logic."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager.get_instance()

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashes password using PBKDF2 with SHA-256 and a random 16-byte salt.
        Format: salt$derived_key (both in hex)
        """
        salt = os.urandom(16).hex()
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100_000
        ).hex()
        return f"{salt}${derived}"

    @staticmethod
    def verify_password(plain_password: str, stored_hash: str) -> bool:
        """
        Verifies plaintext password against stored hash (salt$derived or legacy fallback).
        """
        if not stored_hash:
            return False

        if "$" in stored_hash:
            try:
                salt, expected_derived = stored_hash.split("$", 1)
                actual_derived = hashlib.pbkdf2_hmac(
                    "sha256",
                    plain_password.encode("utf-8"),
                    salt.encode("utf-8"),
                    iterations=100_000
                ).hex()
                return hmac.compare_digest(actual_derived, expected_derived)
            except Exception:
                return False
        else:
            # Fallback for simple legacy test seeds (plain comparison if needed)
            return hmac.compare_digest(plain_password, stored_hash)

    def login(self, raw_username: str, plain_password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Authenticates a user.
        Returns: (success: bool, user_dict: Optional[Dict], message: str)
        """
        normalized_username = ValidationService.normalize_username(raw_username)
        if not normalized_username or not plain_password:
            return False, None, "Please enter both username and password."

        user = self.db.get_user_by_username(normalized_username)
        if not user:
            return False, None, "Invalid username or password."

        if not self.verify_password(plain_password, user["password"]):
            return False, None, "Invalid username or password."

        # Return sanitized user record (excluding password hash)
        user_info = {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "created_at": user["created_at"]
        }
        return True, user_info, f"Welcome back, {user['username']}!"

    def register(
        self,
        raw_username: str,
        password: str,
        confirm_password: str,
        role: str = "patient"
    ) -> Tuple[bool, str]:
        """
        Registers a new user after validating all constraints.
        Returns: (success: bool, message: str)
        """
        # Validate username format
        is_valid_user, user_err = ValidationService.validate_username(raw_username)
        if not is_valid_user:
            return False, user_err

        normalized_username = ValidationService.normalize_username(raw_username)

        # Check if already taken
        if self.db.user_exists(normalized_username):
            return False, f"Username '{normalized_username}' is already taken. Please choose another."

        # Validate password
        is_valid_pass, pass_err = ValidationService.validate_password(password)
        if not is_valid_pass:
            return False, pass_err

        if password != confirm_password:
            return False, "Passwords do not match."

        # Create user with secure hash
        password_hash = self.hash_password(password)
        success = self.db.create_user(normalized_username, password_hash, role=role)
        if success:
            return True, f"Account '{normalized_username}' created successfully! You can now log in."
        else:
            return False, "An error occurred while creating your account. Please try again."

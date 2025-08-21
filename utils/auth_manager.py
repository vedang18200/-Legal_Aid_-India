import hashlib
import streamlit as st
from database.db_manager import execute_query

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user with debugging information"""
    try:
        user_check = execute_query(
            "SELECT id, username, password, user_type FROM users WHERE LOWER(username) = LOWER(%s)",
            (username,),
            fetch='one'
        )

        if not user_check:
            return None

        stored_password = user_check[2]
        hashed_input = hash_password(password)

        if stored_password == hashed_input:
            return (user_check[0], user_check[3])
        else:
            return None

    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

def register_user(username, password, email, phone, location, language, user_type):
    """Register a new user with proper error handling"""
    try:
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = %s",
            (username,),
            fetch='one'
        )

        if existing_user:
            return False, "Username already exists. Please choose a different username."

        existing_email = execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch='one'
        )

        if existing_email:
            return False, "Email already registered. Please use a different email."

        hashed_password = hash_password(password)

        execute_query(
            """INSERT INTO users (username, password, email, phone, location, language, user_type)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (username, hashed_password, email, phone, location, language, user_type)
        )

        return True, "Registration successful!"

    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def validate_registration_data(username, password, confirm_password, email, phone):
    """Validate registration form data"""
    errors = []

    if not all([username, password, confirm_password, email, phone]):
        errors.append("Please fill in all required fields.")

    if password != confirm_password:
        errors.append("Passwords don't match. Please try again.")

    if len(password) < 6:
        errors.append("Password must be at least 6 characters long.")

    if "@" not in email or "." not in email:
        errors.append("Please enter a valid email address.")

    if len(username) < 3:
        errors.append("Username must be at least 3 characters long.")

    return errors

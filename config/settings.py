import streamlit as st

def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Legal Mitra - Access to Justice",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Database configuration
DB_CONFIG = {
    "host": "db.maybtceeuypyuebrqunj.supabase.co",
    "port": "5432",
    "dbname": "postgres",
    "user": "postgres",
    "password_key": "DB_PASSWORD"  # This refers to st.secrets key
}

# Application settings
APP_SETTINGS = {
    "emergency_helpline": "1800-345-4357",
    "nalsa_helpline": "15100",
    "women_helpline": "1091",
    "cyber_crime_helpline": "1930"
}

# Supported languages
SUPPORTED_LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu",
    "Bengali", "Malayalam", "Kannada", "Gujarati", "Marathi"
]

# Legal categories
LEGAL_CATEGORIES = [
    "Family Law", "Criminal Law", "Property Law",
    "Consumer Rights", "Employment Law"
]

# Case priorities
CASE_PRIORITIES = ["Low", "Medium", "High", "Urgent"]

# Case statuses
CASE_STATUSES = ["Open", "In Progress", "Closed", "Pending", "On Hold"]

# Consultation statuses
CONSULTATION_STATUSES = ["Scheduled", "Completed", "Cancelled", "Pending"]

# User types
USER_TYPES = ["Citizen", "Lawyer", "Legal Aid Worker"]

# Locations
MAJOR_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai",
    "Pune", "Hyderabad", "Kolkata", "Other"
]

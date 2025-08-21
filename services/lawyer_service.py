import streamlit as st
import pandas as pd
from database.db_manager import execute_query, get_pg_connection

def get_lawyers(specialization_filter=None, location_filter=None, fee_filter=None):
    """Get filtered list of lawyers with better error handling"""
    try:
        conn = get_pg_connection()
        if conn is None:
            st.error("Unable to connect to database")
            return pd.DataFrame()

        # Base query - ensure we get verified lawyers
        query = """
            SELECT l.*, u.username, u.created_at as user_created_at
            FROM lawyers l
            JOIN users u ON l.user_id = u.id
            WHERE l.verified = %s
        """
        params = [True]

        # Apply filters
        if specialization_filter and specialization_filter != "All":
            query += " AND l.specialization = %s"
            params.append(specialization_filter)

        if location_filter and location_filter != "All":
            query += " AND l.location = %s"
            params.append(location_filter)

        if fee_filter and fee_filter != "All":
            # Parse fee filter and add condition
            fee_conditions = parse_fee_filter(fee_filter)
            if fee_conditions:
                query += f" AND ({fee_conditions})"

        # Order by rating and experience
        query += " ORDER BY l.rating DESC, l.experience DESC"

        lawyers_df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        # Debug info
        st.sidebar.info(f"Debug: Found {len(lawyers_df)} lawyers in database")

        return lawyers_df

    except Exception as e:
        st.error(f"Error loading lawyers: {e}")
        st.sidebar.error(f"SQL Error Details: {str(e)}")
        return pd.DataFrame()

def parse_fee_filter(fee_filter):
    """Parse fee filter into SQL condition"""
    if fee_filter == "₹0-500":
        return "l.fee_range ILIKE '%0-500%' OR l.fee_range ILIKE '%under 500%'"
    elif fee_filter == "₹500-1500":
        return "l.fee_range ILIKE '%500-1500%' OR l.fee_range ILIKE '%500-1000%'"
    elif fee_filter == "₹1500-3000":
        return "l.fee_range ILIKE '%1500-3000%' OR l.fee_range ILIKE '%2000-3000%'"
    elif fee_filter == "₹3000+":
        return "l.fee_range ILIKE '%3000%' OR l.fee_range ILIKE '%above 3000%'"
    return None

def get_lawyer_profile(user_id):
    """Get lawyer profile by user_id with enhanced data"""
    try:
        profile = execute_query(
            """SELECT l.*, u.username, u.email as user_email, u.created_at
               FROM lawyers l
               JOIN users u ON l.user_id = u.id
               WHERE l.user_id = %s""",
            (user_id,), fetch='one'
        )
        return profile
    except Exception as e:
        st.error(f"Error loading lawyer profile: {e}")
        return None

def update_lawyer_profile(user_id, name, email, phone, specialization, experience, location, languages, fee_range=None):
    """Update lawyer profile with verification status handling"""
    try:
        # Check if lawyer profile exists
        existing_profile = execute_query(
            "SELECT id, verified FROM lawyers WHERE user_id = %s",
            (user_id,), fetch='one'
        )

        if existing_profile:
            # Update existing profile - maintain verification status
            execute_query(
                """UPDATE lawyers SET name = %s, email = %s, phone = %s,
                   specialization = %s, experience = %s, location = %s,
                   languages = %s, fee_range = %s, updated_at = NOW()
                   WHERE user_id = %s""",
                (name, email, phone, specialization, experience, location,
                 languages, fee_range, user_id)
            )
        else:
            # Create new profile - set as verified for demo purposes
            # In production, this should be False and require admin approval
            execute_query(
                """INSERT INTO lawyers (user_id, name, email, phone, specialization,
                   experience, location, languages, fee_range, verified, rating, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (user_id, name, email, phone, specialization, experience, location,
                 languages, fee_range, True, 4.5)  # Auto-verify for demo
            )

        return True, "Profile updated successfully! Your profile is now visible in the marketplace."

    except Exception as e:
        return False, f"Error updating profile: {e}"

def get_lawyer_by_id(lawyer_id):
    """Get lawyer details by lawyer table ID with user info"""
    try:
        lawyer = execute_query(
            """SELECT l.*, u.username, u.email as user_email
               FROM lawyers l
               JOIN users u ON l.user_id = u.id
               WHERE l.id = %s""",
            (lawyer_id,), fetch='one'
        )
        return lawyer
    except Exception as e:
        st.error(f"Error fetching lawyer details: {e}")
        return None

def get_lawyer_user_id(lawyer_id):
    """Get user_id from lawyer table ID"""
    try:
        result = execute_query(
            "SELECT user_id FROM lawyers WHERE id = %s",
            (lawyer_id,), fetch='one'
        )
        return result[0] if result else None
    except Exception as e:
        st.error(f"Error getting lawyer user ID: {e}")
        return None

def search_lawyers(search_term, filters=None):
    """Enhanced search with better query"""
    try:
        query = """
            SELECT l.*, u.username
            FROM lawyers l
            JOIN users u ON l.user_id = u.id
            WHERE l.verified = true
            AND (l.name ILIKE %s OR l.specialization ILIKE %s OR l.location ILIKE %s)
        """
        search_pattern = f"%{search_term}%"
        params = [search_pattern, search_pattern, search_pattern]

        if filters:
            if filters.get('specialization') and filters['specialization'] != "All":
                query += " AND l.specialization = %s"
                params.append(filters['specialization'])
            if filters.get('location') and filters['location'] != "All":
                query += " AND l.location = %s"
                params.append(filters['location'])

        query += " ORDER BY l.rating DESC, l.experience DESC"

        lawyers = execute_query(query, params, fetch='all')
        return lawyers if lawyers else []
    except Exception as e:
        st.error(f"Error searching lawyers: {e}")
        return []

def verify_lawyer_profile(user_id):
    """Admin function to verify lawyer profile"""
    try:
        execute_query(
            "UPDATE lawyers SET verified = %s, updated_at = NOW() WHERE user_id = %s",
            (True, user_id)
        )
        return True, "Lawyer profile verified successfully!"
    except Exception as e:
        return False, f"Error verifying profile: {e}"

def get_all_lawyers_for_admin():
    """Get all lawyers for admin verification"""
    try:
        lawyers = execute_query(
            """SELECT l.*, u.username, u.email as user_email
               FROM lawyers l
               JOIN users u ON l.user_id = u.id
               ORDER BY l.created_at DESC""",
            fetch='all'
        )
        return lawyers if lawyers else []
    except Exception as e:
        st.error(f"Error fetching lawyers for admin: {e}")
        return []

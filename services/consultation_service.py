import streamlit as st
from datetime import datetime
from database.db_manager import execute_query

def validate_lawyer_exists(user_id):
    """
    Check if lawyer profile exists, create if not
    """
    try:
        lawyer_record = execute_query(
            "SELECT id FROM lawyers WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )

        if not lawyer_record:
            # Create basic profile
            success = create_basic_lawyer_profile(user_id)
            if success:
                st.info("ℹ️ Basic lawyer profile created. Please complete your profile in the Profile section.")
            return success

        return True

    except Exception as e:
        st.error(f"Error validating lawyer: {e}")
        return False


def schedule_consultation(client_user_id, lawyer_user_id, consultation_datetime, fee_amount, notes):
    """
    Schedule a new consultation with proper lawyer_id validation
    """
    try:
        # First, get the actual lawyer_id from the lawyers table using user_id
        lawyer_record = execute_query(
            "SELECT id FROM lawyers WHERE user_id = %s",
            (lawyer_user_id,),
            fetch='one'
        )

        if not lawyer_record:
            # If lawyer profile doesn't exist, create it first
            create_lawyer_profile_result = create_basic_lawyer_profile(lawyer_user_id)
            if not create_lawyer_profile_result:
                return False, "❌ Lawyer profile not found and could not be created. Please complete your lawyer profile first."

            # Try to get the lawyer_id again
            lawyer_record = execute_query(
                "SELECT id FROM lawyers WHERE user_id = %s",
                (lawyer_user_id,),
                fetch='one'
            )

            if not lawyer_record:
                return False, "❌ Could not find or create lawyer profile."

        lawyer_id = lawyer_record[0]

        # Get client user_id (in case client_user_id is actually user_id)
        client_id = client_user_id

        # Insert consultation with proper lawyer_id
        consultation_id = execute_query(
            """
            INSERT INTO consultations (user_id, lawyer_id, consultation_type, status,
                                     scheduled_at, consultation_date, fee_amount, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (client_id, lawyer_id, 'Scheduled', 'Pending',
             consultation_datetime, consultation_datetime, fee_amount, notes),
            fetch='one'
        )

        if consultation_id:
            return True, f"✅ Consultation scheduled successfully (ID: {consultation_id[0]})"
        else:
            return False, "❌ Failed to schedule consultation"

    except Exception as e:
        return False, f"❌ Error scheduling consultation: {str(e)}"

def get_user_consultations(user_id):
    """Get all consultations for a user"""
    try:
        consultations = execute_query(
            """SELECT c.id, c.consultation_date, c.status, c.notes, c.fee_amount,
                      l.name as lawyer_name, l.phone as lawyer_phone
               FROM consultations c
               JOIN lawyers l ON c.lawyer_id = l.user_id
               WHERE c.user_id = %s
               ORDER BY c.consultation_date DESC""",
            (user_id,), fetch='all'
        )
        return consultations if consultations else []
    except Exception as e:
        st.error(f"Error fetching consultations: {e}")
        return []

def get_lawyer_consultations(lawyer_user_id, upcoming_only=False):
    """Get consultations for a lawyer using user_id"""
    try:
        query = """
            SELECT c.id, c.consultation_date, c.status, c.notes, c.fee_amount,
                   u.username, u.phone, u.email
            FROM consultations c
            JOIN users u ON c.user_id = u.id
            JOIN lawyers l ON c.lawyer_id = l.id
            WHERE l.user_id = %s
        """
        if upcoming_only:
            query += " AND c.consultation_date > NOW()"

        query += " ORDER BY c.consultation_date ASC"

        consultations = execute_query(query, (lawyer_user_id,), fetch='all')
        return consultations if consultations else []
    except Exception as e:
        st.error(f"Error fetching lawyer consultations: {e}")
        return []

def update_consultation_status(consultation_id, new_status):
    """
    Update consultation status
    """
    try:
        result = execute_query(
            "UPDATE consultations SET status = %s WHERE id = %s",
            (new_status, consultation_id),
            fetch=False
        )
        return True
    except Exception as e:
        st.error(f"Error updating consultation status: {e}")
        return False

def get_consultation_statistics(lawyer_id):
    """Get consultation statistics for a lawyer"""
    try:
        stats = {}

        # Pending consultations
        pending = execute_query(
            "SELECT COUNT(*) FROM consultations WHERE lawyer_id = %s AND status = 'Pending'",
            (lawyer_id,), fetch='one'
        )
        stats['pending_consultations'] = pending[0] if pending else 0

        # Upcoming consultations
        upcoming = execute_query(
            "SELECT COUNT(*) FROM consultations WHERE lawyer_id = %s AND consultation_date > NOW()",
            (lawyer_id,), fetch='one'
        )
        stats['upcoming_consultations'] = upcoming[0] if upcoming else 0

        # Completed this month
        completed = execute_query(
            """SELECT COUNT(*) FROM consultations
               WHERE lawyer_id = %s AND status = 'Completed'
               AND DATE_TRUNC('month', consultation_date) = DATE_TRUNC('month', NOW())""",
            (lawyer_id,), fetch='one'
        )
        stats['completed_this_month'] = completed[0] if completed else 0

        return stats
    except Exception as e:
        st.error(f"Error getting consultation statistics: {e}")
        return {}

def get_lawyer_clients(user_id):
    """
    Get clients for a lawyer
    """
    try:
        # First get the lawyer_id
        lawyer_record = execute_query(
            "SELECT id FROM lawyers WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )

        if not lawyer_record:
            return []

        lawyer_id = lawyer_record[0]

        # Get unique clients from cases and consultations
        clients = execute_query(
            """
            SELECT DISTINCT u.id, u.username, u.email, u.phone
            FROM users u
            WHERE u.id IN (
                SELECT DISTINCT user_id FROM cases WHERE lawyer_id = %s
                UNION
                SELECT DISTINCT user_id FROM consultations WHERE lawyer_id = %s
            )
            ORDER BY u.username
            """,
            (lawyer_id, lawyer_id),
            fetch='all'
        )

        return clients or []

    except Exception as e:
        st.error(f"Error getting lawyer clients: {e}")
        return []
def get_lawyer_consultations(user_id, upcoming_only=False):
    """
    Get consultations for a lawyer with proper joins
    """
    try:
        # First get the lawyer_id
        lawyer_record = execute_query(
            "SELECT id FROM lawyers WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )

        if not lawyer_record:
            return []

        lawyer_id = lawyer_record[0]

        # Get consultations
        if upcoming_only:
            query = """
                SELECT c.id, c.consultation_date, c.status, c.notes, c.fee_amount,
                       u.username, u.phone, u.email
                FROM consultations c
                JOIN users u ON c.user_id = u.id
                WHERE c.lawyer_id = %s AND c.consultation_date >= %s
                ORDER BY c.consultation_date ASC
            """
            params = (lawyer_id, datetime.now())
        else:
            query = """
                SELECT c.id, c.consultation_date, c.status, c.notes, c.fee_amount,
                       u.username, u.phone, u.email
                FROM consultations c
                JOIN users u ON c.user_id = u.id
                WHERE c.lawyer_id = %s
                ORDER BY c.consultation_date DESC
            """
            params = (lawyer_id,)

        return execute_query(query, params, fetch='all') or []

    except Exception as e:
        st.error(f"Error getting lawyer consultations: {e}")
        return []

def create_basic_lawyer_profile(user_id):
    """
    Create a basic lawyer profile if it doesn't exist
    """
    try:
        # Get user information
        user_info = execute_query(
            "SELECT username, email FROM users WHERE id = %s",
            (user_id,),
            fetch='one'
        )

        if not user_info:
            return False

        username, email = user_info

        # Create basic lawyer profile
        lawyer_id = execute_query(
            """
            INSERT INTO lawyers (user_id, name, email, specialization, experience,
                               location, verified, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (user_id, username, email, 'General Practice', 0,
             'Not Specified', False, datetime.now()),
            fetch='one'
        )

        return lawyer_id is not None

    except Exception as e:
        st.error(f"Error creating basic lawyer profile: {e}")
        return False

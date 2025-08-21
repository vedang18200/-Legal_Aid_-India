import streamlit as st
from datetime import datetime
from database.db_manager import execute_query

def create_case(user_id, title, description, category, priority):
    """Create a new case"""
    try:
        execute_query(
            """INSERT INTO cases (user_id, title, description, category, status, priority, created_at)
               VALUES (%s, %s, %s, %s, 'Open', %s, %s)""",
            (user_id, title, description, category, priority, datetime.now())
        )
        return True, "Case created successfully!"
    except Exception as e:
        return False, f"Error creating case: {e}"

def get_user_cases(user_id, status_filter=None, category_filter=None):
    """Get cases for a specific user with optional filters"""
    try:
        query = """
            SELECT c.id, c.user_id, c.lawyer_id, c.title, c.description,
                   c.category, c.status, c.priority, c.created_at, c.updated_at,
                   u.username as lawyer_name
            FROM cases c
            LEFT JOIN users u ON c.lawyer_id = u.id
            WHERE c.user_id = %s
        """
        params = [user_id]

        if status_filter and status_filter != "All":
            query += " AND c.status = %s"
            params.append(status_filter)

        if category_filter and category_filter != "All":
            query += " AND c.category = %s"
            params.append(category_filter)

        query += " ORDER BY c.created_at DESC"

        return execute_query(query, params, fetch='all')
    except Exception as e:
        st.error(f"Error fetching user cases: {e}")
        return []

def get_lawyer_cases(lawyer_user_id, status_filter=None, category_filter=None, priority_filter=None):
    """Get cases assigned to a specific lawyer using user_id"""
    try:
        query = """
            SELECT c.id, c.title, c.description, c.category, c.status, c.priority,
                c.created_at, c.updated_at, u.username as client_name, u.phone, u.email, c.user_id
            FROM cases c
            JOIN users u ON c.user_id = u.id
            JOIN lawyers l ON c.lawyer_id = l.id
            WHERE l.user_id = %s
        """
        params = [lawyer_user_id]

        if status_filter and status_filter != "All":
            query += " AND c.status = %s"
            params.append(status_filter)
        if category_filter and category_filter != "All":
            query += " AND c.category = %s"
            params.append(category_filter)
        if priority_filter and priority_filter != "All":
            query += " AND c.priority = %s"
            params.append(priority_filter)

        query += " ORDER BY c.updated_at DESC"

        return execute_query(query, params, fetch='all')
    except Exception as e:
        st.error(f"Error fetching lawyer cases: {e}")
        return []

def get_available_cases():
    """Get unassigned cases available for lawyers to take"""
    try:
        cases = execute_query(
            """SELECT c.id, c.title, c.description, c.category, c.priority,
                      c.created_at, u.username, u.location
               FROM cases c
               JOIN users u ON c.user_id = u.id
               WHERE c.lawyer_id IS NULL AND c.status = 'Open'
               ORDER BY c.created_at DESC""",
            fetch='all'
        )
        return cases if cases else []
    except Exception as e:
        st.error(f"Error fetching available cases: {e}")
        return []

def assign_case_to_lawyer(case_id, lawyer_user_id):
    """Assign a case to a lawyer using lawyer's user_id"""
    try:
        # First get the lawyer's ID from the lawyers table
        lawyer_result = execute_query(
            "SELECT id FROM lawyers WHERE user_id = %s",
            (lawyer_user_id,), fetch='one'
        )

        if not lawyer_result:
            return False, "Lawyer profile not found"

        lawyer_id = lawyer_result[0]

        # Now assign the case
        execute_query(
            "UPDATE cases SET lawyer_id = %s, status = 'In Progress', updated_at = %s WHERE id = %s",
            (lawyer_id, datetime.now(), case_id)
        )
        return True, "Case assigned successfully!"
    except Exception as e:
        return False, f"Error assigning case: {e}"

def get_lawyer_cases(lawyer_user_id, status_filter=None, category_filter=None, priority_filter=None):
    """Get cases assigned to a specific lawyer using user_id"""
    try:
        query = """
            SELECT c.id, c.title, c.description, c.category, c.status, c.priority,
                c.created_at, c.updated_at, u.username as client_name, u.phone, u.email, c.user_id
            FROM cases c
            JOIN users u ON c.user_id = u.id
            JOIN lawyers l ON c.lawyer_id = l.id
            WHERE l.user_id = %s
        """
        params = [lawyer_user_id]

        if status_filter and status_filter != "All":
            query += " AND c.status = %s"
            params.append(status_filter)
        if category_filter and category_filter != "All":
            query += " AND c.category = %s"
            params.append(category_filter)
        if priority_filter and priority_filter != "All":
            query += " AND c.priority = %s"
            params.append(priority_filter)

        query += " ORDER BY c.updated_at DESC"

        return execute_query(query, params, fetch='all')
    except Exception as e:
        st.error(f"Error fetching lawyer cases: {e}")
        return []

def update_case_status(case_id, new_status):
    """Update case status"""
    try:
        execute_query(
            "UPDATE cases SET status = %s, updated_at = %s WHERE id = %s",
            (new_status, datetime.now(), case_id)
        )
        return True, f"Case status updated to: {new_status}"
    except Exception as e:
        return False, f"Error updating status: {e}"

def get_case_statistics(user_id, user_type):
    """Get case statistics based on user type"""
    try:
        if user_type == "Lawyer":
            stats = {}

            # Active cases
            active = execute_query(
                "SELECT COUNT(*) FROM cases WHERE lawyer_id = %s AND status IN ('Open', 'In Progress')",
                (user_id,), fetch='one'
            )
            stats['active_cases'] = active[0] if active else 0

            # Total clients
            clients = execute_query(
                "SELECT COUNT(DISTINCT user_id) FROM cases WHERE lawyer_id = %s",
                (user_id,), fetch='one'
            )
            stats['total_clients'] = clients[0] if clients else 0

            # Available cases
            available = execute_query(
                "SELECT COUNT(*) FROM cases WHERE lawyer_id IS NULL AND status = 'Open'",
                fetch='one'
            )
            stats['available_cases'] = available[0] if available else 0

            return stats

        elif user_type == "Citizen":
            stats = {}

            # User's cases
            total = execute_query(
                "SELECT COUNT(*) FROM cases WHERE user_id = %s",
                (user_id,), fetch='one'
            )
            stats['total_cases'] = total[0] if total else 0

            # Active cases
            active = execute_query(
                "SELECT COUNT(*) FROM cases WHERE user_id = %s AND status IN ('Open', 'In Progress')",
                (user_id,), fetch='one'
            )
            stats['active_cases'] = active[0] if active else 0

            return stats

    except Exception as e:
        st.error(f"Error getting statistics: {e}")
        return {}

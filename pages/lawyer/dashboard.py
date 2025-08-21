
import streamlit as st
from services.case_service import get_case_statistics
from services.consultation_service import get_consultation_statistics, get_lawyer_consultations
from database.db_manager import execute_query
from config.styles import apply_custom_styles

def show_lawyer_dashboard():
    """Display lawyer dashboard"""
    apply_custom_styles()
    st.title("💼 Lawyer Dashboard")

    # Welcome message
    st.markdown(f"### Welcome back, Advocate {st.session_state.get('username', 'User')}!")

    render_quick_stats()
    render_recent_activities()

def render_quick_stats():
    """Render quick statistics for lawyers"""
    col1, col2, col3, col4 = st.columns(4)

    # Get statistics
    case_stats = get_case_statistics(st.session_state.user_id, "Lawyer")
    consultation_stats = get_consultation_statistics(st.session_state.user_id)

    with col1:
        st.metric("Active Cases", case_stats.get('active_cases', 0))

    with col2:
        st.metric("Pending Consultations", consultation_stats.get('pending_consultations', 0))

    with col3:
        st.metric("Total Clients", case_stats.get('total_clients', 0))

    with col4:
        st.metric("Available Cases", case_stats.get('available_cases', 0))

def render_recent_activities():
    """Render recent activities section"""
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        render_recent_cases()

    with col2:
        render_upcoming_appointments()

def render_recent_cases():
    """Render recent case updates"""
    st.subheader("🔄 Recent Case Updates")

    try:
        recent_cases = execute_query("""
            SELECT c.title, c.status, c.updated_at, u.username as client_name
            FROM cases c
            JOIN users u ON c.user_id = u.id
            WHERE c.lawyer_id = %s
            ORDER BY c.updated_at DESC LIMIT 5
        """, (st.session_state.user_id,), fetch='all')

        if recent_cases:
            for case in recent_cases:
                title, status, updated_at, client_name = case
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0;
                            border-radius: 5px; background-color: rgb(14, 17, 23); color: white;">
                    <strong>{title}</strong><br>
                    Client: {client_name} | Status: {status}<br>
                    <small>Updated: {updated_at}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent case updates")
    except Exception as e:
        st.error(f"Error loading recent cases: {e}")

def render_upcoming_appointments():
    """Render upcoming appointments"""
    st.subheader("📅 Upcoming Appointments")

    try:
        upcoming_appointments = get_lawyer_consultations(st.session_state.user_id, upcoming_only=True)

        if upcoming_appointments:
            for appointment in upcoming_appointments[:5]:  # Show only first 5
                consultation_id, date, status, notes, fee, client_name, phone, email = appointment
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0;
                            border-radius: 5px; background-color: rgb(14, 17, 23); color: white;">
                    <strong>{client_name}</strong><br>
                    Date: {date}<br>
                    <small>{notes or 'No notes'}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming appointments")
    except Exception as e:
        st.error(f"Error loading appointments: {e}")


# ==========================================

# pages/lawyer/appointments.py
import streamlit as st
from datetime import datetime, timedelta, date, time
from services.consultation_service import (
    get_lawyer_consultations, update_consultation_status,
    schedule_consultation, get_lawyer_clients
)
from config.styles import apply_custom_styles, STATUS_COLORS

def show_lawyer_appointments():
    """Display lawyer appointments page"""
    apply_custom_styles()
    st.title("📅 Appointments & Consultations")

    tab1, tab2, tab3 = st.tabs(["Upcoming", "Past", "Schedule New"])

    with tab1:
        render_upcoming_appointments()

    with tab2:
        render_past_appointments()

    with tab3:
        render_schedule_form()

def render_upcoming_appointments():
    """Render upcoming appointments"""
    st.subheader("📅 Upcoming Appointments")
    try:
        upcoming = get_lawyer_consultations(st.session_state.user_id, upcoming_only=True)

        if upcoming:
            for appointment in upcoming:
                consultation_id, date, status, notes, fee, client_name, phone, email = appointment
                st.markdown(f"""
                <div style="border: 1px solid #007bff; padding: 15px; margin: 10px 0; border-radius: 10px;">
                    <h4>📅 {date}</h4>
                    <p><strong>Client:</strong> {client_name} | <strong>Status:</strong> {status}</p>
                    <p><strong>Contact:</strong> {phone} | {email}</p>
                    <p><strong>Fee:</strong> ₹{fee or 'TBD'} | <strong>Notes:</strong> {notes or 'None'}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Mark Complete", key=f"complete_{consultation_id}"):
                        update_consultation_status(consultation_id, 'Completed')
                        st.success("Appointment marked as completed")
                        st.rerun()
                with col2:
                    if st.button(f"Reschedule", key=f"reschedule_{consultation_id}"):
                        st.info("Reschedule feature - to be implemented")
                with col3:
                    if st.button(f"Cancel", key=f"cancel_{consultation_id}"):
                        update_consultation_status(consultation_id, 'Cancelled')
                        st.warning("Appointment cancelled")
                        st.rerun()
        else:
            st.info("No upcoming appointments")
    except Exception as e:
        st.error(f"Error loading upcoming appointments: {e}")

def render_past_appointments():
    """Render past appointments"""
    st.subheader("📋 Past Appointments")
    try:
        past = get_lawyer_consultations(st.session_state.user_id, upcoming_only=False)

        # Filter only past appointments
        past_appointments = [apt for apt in past if apt[1] < datetime.now()]

        if past_appointments:
            for appointment in past_appointments[:10]:  # Show last 10
                date, status, client_name, fee = appointment[1], appointment[2], appointment[5], appointment[4]
                st.markdown(f"**{date}** - {client_name} | {status} | ₹{fee or 'Free'}")
        else:
            st.info("No past appointments")
    except Exception as e:
        st.error(f"Error loading past appointments: {e}")

def render_schedule_form():
    """Render consultation scheduling form with proper date/time input"""
    st.subheader("➕ Schedule New Consultation")

    # First, validate that lawyer profile exists
    from services.consultation_service import validate_lawyer_exists
    if not validate_lawyer_exists(st.session_state.user_id):
        st.error("❌ Lawyer profile not found. Please complete your profile first.")
        if st.button("Go to Profile"):
            st.session_state.current_page = "Lawyer Profile"
            st.rerun()
        return

    with st.form("schedule_consultation"):
        # Get list of clients
        try:
            clients = get_lawyer_clients(st.session_state.user_id)

            if clients:
                client_options = {f"{client[1]} (ID: {client[0]})": client[0] for client in clients}
                selected_client = st.selectbox("Select Client", list(client_options.keys()))

                # FIXED: Replace st.datetime_input with separate date and time inputs
                col1, col2 = st.columns(2)

                with col1:
                    consultation_date = st.date_input(
                        "Consultation Date",
                        min_value=date.today() + timedelta(days=1),
                        value=date.today() + timedelta(days=1)
                    )

                with col2:
                    # Time slots for better UX
                    time_slots = [
                        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                        "12:00", "12:30", "14:00", "14:30", "15:00", "15:30",
                        "16:00", "16:30", "17:00", "17:30", "18:00"
                    ]

                    selected_time_str = st.selectbox(
                        "Consultation Time",
                        time_slots,
                        index=0
                    )

                    # Convert to time object
                    hour, minute = map(int, selected_time_str.split(':'))
                    consultation_time = time(hour, minute)

                # Combine date and time into datetime
                consultation_datetime = datetime.combine(consultation_date, consultation_time)

                fee_amount = st.number_input("Fee Amount (₹)", min_value=0, value=500)
                notes = st.text_area("Notes", placeholder="Additional notes for the consultation...")

                submitted = st.form_submit_button("📅 Schedule Consultation", type="primary")

                if submitted:
                    client_id = client_options[selected_client]
                    success, message = schedule_consultation(
                        client_id, st.session_state.user_id,
                        consultation_datetime, fee_amount, notes
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No clients found. Clients will appear here once they have cases assigned to you.")

        except Exception as e:
            st.error(f"Error in schedule form: {e}")

def render_alternative_schedule_form():
    """Alternative scheduling form with manual time input"""
    st.subheader("➕ Schedule New Consultation (Alternative)")

    with st.form("alt_schedule_consultation"):
        try:
            clients = get_lawyer_clients(st.session_state.user_id)

            if clients:
                client_options = {f"{client[1]} (ID: {client[0]})": client[0] for client in clients}
                selected_client = st.selectbox("Select Client", list(client_options.keys()))

                # Alternative approach: Use date_input and time_input separately
                consultation_date = st.date_input(
                    "Consultation Date",
                    min_value=date.today() + timedelta(days=1),
                    value=date.today() + timedelta(days=1)
                )

                consultation_time = st.time_input(
                    "Consultation Time",
                    value=time(10, 0)  # Default to 10:00 AM
                )

                # Combine date and time
                consultation_datetime = datetime.combine(consultation_date, consultation_time)

                fee_amount = st.number_input("Fee Amount (₹)", min_value=0, value=500)
                notes = st.text_area("Notes")

                submitted = st.form_submit_button("📅 Schedule Consultation")

                if submitted:
                    client_id = client_options[selected_client]
                    success, message = schedule_consultation(
                        client_id, st.session_state.user_id,
                        consultation_datetime, fee_amount, notes
                    )
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.info("No clients found. Clients will appear here once they have cases assigned to you.")

        except Exception as e:
            st.error(f"Error in alternative schedule form: {e}")

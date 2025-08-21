# ===========================================
# FILE: pages/lawyer/lawyer_cases.py
# ===========================================

import streamlit as st
from services.case_service import get_lawyer_cases, update_case_status
from config.settings import CASE_STATUSES, LEGAL_CATEGORIES, CASE_PRIORITIES
from config.styles import apply_custom_styles, STATUS_COLORS

def show_lawyer_cases():
    """Display lawyer's cases management page"""
    apply_custom_styles()
    st.title("📋 My Cases Management")

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + CASE_STATUSES)
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + LEGAL_CATEGORIES)
    with col3:
        priority_filter = st.selectbox("Filter by Priority", ["All"] + CASE_PRIORITIES)

    try:
        cases = get_lawyer_cases(
            st.session_state.user_id,
            status_filter,
            category_filter,
            priority_filter
        )

        if not cases:
            st.info("No cases found matching your criteria.")
            return

        # Display cases
        for case in cases:
            render_lawyer_case_card(case)

    except Exception as e:
        st.error(f"Error loading cases: {e}")

def render_lawyer_case_card(case):
    """Render lawyer case card with management options"""
    case_id, title, description, category, status, priority, created_at, updated_at, client_name, phone, email, client_user_id = case

    status_color = STATUS_COLORS.get(status, '#6c757d')

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #212529;">
        <h4>{title} <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{status}</span></h4>
        <p><strong>Client:</strong> {client_name} | <strong>Category:</strong> {category} | <strong>Priority:</strong> {priority}</p>
        <p><strong>Description:</strong> {description}</p>
        <p><strong>Contact:</strong> {phone} | {email}</p>
        <p><small><strong>Created:</strong> {created_at} | <strong>Updated:</strong> {updated_at}</small></p>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Status update dropdown
        current_index = CASE_STATUSES.index(status) if status in CASE_STATUSES else 0
        new_status = st.selectbox("Update Status", CASE_STATUSES,
                                index=current_index, key=f"status_select_{case_id}")
        if st.button("Update", key=f"status_update_{case_id}"):
            success, message = update_case_status(case_id, new_status)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button(f"Add Notes", key=f"notes_{case_id}"):
            st.info("Notes feature - to be implemented")

    with col3:
        if st.button(f"Schedule Meeting", key=f"meeting_{case_id}"):
            st.info("Meeting scheduling - to be implemented")

    with col4:
        if st.button(f"Contact Client", key=f"contact_{case_id}"):
            st.session_state.chat_with = client_user_id
            st.session_state.chat_with_name = client_name
            st.session_state.current_page = "Messages"
            st.rerun()

# ===========================================
# FILE: pages/lawyer/clients.py
# ===========================================

import streamlit as st
from services.consultation_service import get_lawyer_clients
from config.styles import apply_custom_styles

def show_lawyer_clients():
    """Display lawyer's clients page"""
    apply_custom_styles()
    st.title("👥 My Clients")

    try:
        clients = get_lawyer_clients(st.session_state.user_id)

        if not clients:
            st.info("You don't have any clients yet.")
            return

        for client in clients:
            render_client_card(client)

    except Exception as e:
        st.error(f"Error loading clients: {e}")

def render_client_card(client):
    """Render individual client card"""
    user_id, username, email, phone, location, total_cases, active_cases = client

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px;">
        <h4>👤 {username}</h4>
        <p><strong>📧 Email:</strong> {email} | <strong>📱 Phone:</strong> {phone}</p>
        <p><strong>📍 Location:</strong> {location}</p>
        <p><strong>📊 Cases:</strong> {total_cases} total, {active_cases} active</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"View Cases", key=f"view_cases_{user_id}"):
            st.info(f"Showing cases for {username}")
    with col2:
        if st.button(f"Schedule Consultation", key=f"schedule_{user_id}"):
            st.info(f"Scheduling consultation with {username}")
    with col3:
        if st.button(f"Send Message", key=f"message_{user_id}"):
            st.session_state.chat_with = user_id
            st.session_state.chat_with_name = username
            st.session_state.current_page = "Messages"
            st.rerun()

# ===========================================
# FILE: pages/lawyer/appointments.py
# ===========================================

import streamlit as st
from datetime import datetime, timedelta
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

def render_past_appointments():
    """Render past appointments"""
    st.subheader("📋 Past Appointments")
    past = get_lawyer_consultations(st.session_state.user_id, upcoming_only=False)

    # Filter only past appointments
    past_appointments = [apt for apt in past if apt[1] < datetime.now()]

    if past_appointments:
        for appointment in past_appointments[:10]:  # Show last 10
            date, status, client_name, fee = appointment[1], appointment[2], appointment[5], appointment[4]
            st.markdown(f"**{date}** - {client_name} | {status} | ₹{fee or 'Free'}")
    else:
        st.info("No past appointments")

def render_schedule_form():
    """Render consultation scheduling form"""
    st.subheader("➕ Schedule New Consultation")
    with st.form("schedule_consultation"):
        # Get list of clients
        clients = get_lawyer_clients(st.session_state.user_id)

        if clients:
            client_options = {f"{client[1]} (ID: {client[0]})": client[0] for client in clients}
            selected_client = st.selectbox("Select Client", list(client_options.keys()))
            consultation_date = st.datetime_input("Consultation Date & Time",
                                                value=datetime.now() + timedelta(days=1))
            fee_amount = st.number_input("Fee Amount (₹)", min_value=0, value=500)
            notes = st.text_area("Notes")

            if st.form_submit_button("Schedule Consultation"):
                client_id = client_options[selected_client]
                success, message = schedule_consultation(
                    client_id, st.session_state.user_id,
                    consultation_date, fee_amount, notes
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        else:
            st.info("No clients found. Clients will appear here once they have cases assigned to you.")

# ===========================================
# FILE: pages/lawyer/earnings.py
# ===========================================

import streamlit as st
from config.styles import apply_custom_styles

def show_lawyer_earnings():
    """Display lawyer earnings page"""
    apply_custom_styles()
    st.title("💰 Earnings Dashboard")
    st.info("📊 Earnings tracking and analytics features coming soon!")

    # Placeholder earnings display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("This Month", "₹25,000", "12%")
    with col2:
        st.metric("Last Month", "₹22,300", "-5%")
    with col3:
        st.metric("Total Earnings", "₹2,45,000")
    with col4:
        st.metric("Pending Payments", "₹8,500")

# ===========================================
# FILE: pages/lawyer/resources.py
# ===========================================

import streamlit as st
from config.styles import apply_custom_styles

def show_lawyer_resources():
    """Display lawyer resources page"""
    apply_custom_styles()
    st.title("⚖️ Legal Resources")
    st.info("📚 Legal resources and reference materials coming soon!")

    # Placeholder content
    with st.expander("📖 Case Law Database"):
        st.markdown("Access to latest case laws and judgments")

    with st.expander("📋 Legal Forms & Templates"):
        st.markdown("Downloadable legal forms and document templates")

    with st.expander("📰 Legal News & Updates"):
        st.markdown("Latest legal news and regulatory updates")

# ===========================================
# FILE: pages/lawyer/lawyer_profile.py
# ===========================================

import streamlit as st
from services.lawyer_service import get_lawyer_profile, update_lawyer_profile
from config.settings import LEGAL_CATEGORIES, MAJOR_CITIES, SUPPORTED_LANGUAGES
from config.styles import apply_custom_styles

def show_lawyer_profile():
    """Display lawyer profile management page"""
    apply_custom_styles()
    st.title("👤 Lawyer Profile Management")

    try:
        profile = get_lawyer_profile(st.session_state.user_id)

        if profile:
            name, email, phone, specialization, experience, location, languages, username = profile
        else:
            name = email = phone = specialization = location = languages = ""
            experience = 0
            username = st.session_state.get('username', '')

        render_profile_form(name, email, phone, specialization, experience, location, languages, username)

    except Exception as e:
        st.error(f"Error loading profile: {e}")

def render_profile_form(name, email, phone, specialization, experience, location, languages, username):
    """Render lawyer profile form"""
    with st.form("lawyer_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name", value=name)
            phone_input = st.text_input("Phone", value=phone or "")
            specialization_input = st.selectbox("Specialization", LEGAL_CATEGORIES,
                index=LEGAL_CATEGORIES.index(specialization) if specialization in LEGAL_CATEGORIES else 0)
            languages_input = st.text_input("Languages", value=languages or "")

        with col2:
            experience_input = st.number_input("Years of Experience", min_value=0, max_value=50, value=experience or 0)
            location_input = st.selectbox("Location", MAJOR_CITIES,
                index=MAJOR_CITIES.index(location) if location in MAJOR_CITIES else 0)
            email_input = st.text_input("Email", value=email or "")
            registration = st.text_input("Bar Council Registration", placeholder="Registration Number")

        bio = st.text_area("Bio/Description", placeholder="Brief description of your practice and expertise")

        if st.form_submit_button("Update Profile"):
            success, message = update_lawyer_profile(
                st.session_state.user_id, full_name, email_input, phone_input,
                specialization_input, experience_input, location_input, languages_input
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

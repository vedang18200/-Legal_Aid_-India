import streamlit as st
from pages.public import home, chatbot, legal_awareness, login
from pages.citizen import cases, consultations, profile
from pages.lawyer import dashboard, available_cases, lawyer_cases, clients, appointments, earnings, resources, lawyer_profile,lawyer_marketplace
from pages.messaging import messages
from pages.admin import admin_dashboard

# Make sure user is authenticated before showing lawyer-specific pages
if st.session_state.get('current_page') in ['Available Cases', 'My Cases', 'Clients', 'Appointments']:
    if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'Lawyer':
        st.warning("Access denied. This page is for lawyers only.")
        st.session_state.current_page = 'Home'
        st.rerun()
        
def route_to_page():
    """Route to the appropriate page based on current_page in session state"""
    current_page = st.session_state.current_page

    # Public pages (accessible to all)
    if current_page == "Home":
        from pages.public.home import show_home_page
        show_home_page()
    elif current_page == "Chatbot":
        from pages.public.chatbot import show_chatbot_page
        show_chatbot_page()
    elif current_page == "Lawyers":
        from pages.lawyer.lawyer_marketplace import show_lawyer_marketplace
        show_lawyer_marketplace()
    elif current_page == "Awareness":
        from pages.public.legal_awareness import show_legal_awareness
        show_legal_awareness()
    elif current_page == "Login":
        from pages.public.login import show_login_page
        show_login_page()

    # Citizen-specific pages
    elif current_page == "Cases":
        from pages.citizen.cases import show_case_tracking
        show_case_tracking()
    elif current_page == "Consultations":
        from pages.citizen.consultations import show_consultations_page
        show_consultations_page()
    elif current_page == "Profile":
        from pages.citizen.profile import show_profile_page
        show_profile_page()

    # Messaging (available to all authenticated users)
    elif current_page == "Messages":
        from pages.messaging.messages import show_messages_page
        show_messages_page()

    # Lawyer-specific pages
    elif current_page == "LawyerDashboard":
        from pages.lawyer.dashboard import show_lawyer_dashboard
        show_lawyer_dashboard()
    elif current_page == "AvailableCases":
        from pages.lawyer.available_cases import show_available_cases
        show_available_cases()
    elif current_page == "LawyerCases":
        from pages.lawyer.lawyer_cases import show_lawyer_cases
        show_lawyer_cases()
    elif current_page == "LawyerClients":
        from pages.lawyer.clients import show_lawyer_clients
        show_lawyer_clients()
    elif current_page == "LawyerAppointments":
        from pages.lawyer.appointments import show_lawyer_appointments
        show_lawyer_appointments()
    elif current_page == "LawyerEarnings":
        from pages.lawyer.earnings import show_lawyer_earnings
        show_lawyer_earnings()
    elif current_page == "LawyerResources":
        from pages.lawyer.resources import show_lawyer_resources
        show_lawyer_resources()
    elif current_page == "LawyerProfile":
        from pages.lawyer.lawyer_profile import show_lawyer_profile
        show_lawyer_profile()

    # Admin pages
    elif current_page.startswith("Admin"):
        from pages.admin.admin_dashboard import show_admin_pages
        show_admin_pages(current_page)

    # Default fallback
    else:
        st.error(f"Page not found: {current_page}")
        st.session_state.current_page = "Home"
        st.rerun()

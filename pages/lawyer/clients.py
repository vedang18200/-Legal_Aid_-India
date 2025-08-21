
# pages/lawyer/clients.py
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

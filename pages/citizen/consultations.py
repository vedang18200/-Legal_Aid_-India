import streamlit as st
from services.consultation_service import get_user_consultations
from config.styles import apply_custom_styles, STATUS_COLORS

def show_consultations_page():
    """Display user consultations page"""
    apply_custom_styles()
    st.title("📅 My Consultations")

    if not st.session_state.authenticated:
        st.warning("Please login to view consultations")
        return

    try:
        consultations = get_user_consultations(st.session_state.user_id)

        if consultations:
            st.subheader("Your Consultations")
            for consultation in consultations:
                render_consultation_card(consultation)
        else:
            st.info("No consultations booked yet.")
            render_booking_help()

    except Exception as e:
        st.error(f"Error loading consultations: {e}")

def render_consultation_card(consultation):
    """Render individual consultation card"""
    consultation_id, date, status, notes, fee, lawyer_name, lawyer_phone = consultation

    # Determine status color
    status_color = STATUS_COLORS.get(status, '#6c757d')

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #212529;">
        <h4>Consultation with {lawyer_name} <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{status}</span></h4>
        <p><strong>Date:</strong> {date} | <strong>Fee:</strong> ₹{fee or 'TBD'}</p>
        <p><strong>Notes:</strong> {notes or 'No notes'}</p>
        <p><strong>Lawyer Contact:</strong> {lawyer_phone}</p>
    </div>
    """, unsafe_allow_html=True)

def render_booking_help():
    """Render help information for booking consultations"""
    st.markdown("""
    ### 📖 How to Book a Consultation:
    1. Go to **Find Lawyers** page
    2. Browse and select a lawyer
    3. Click **Book Consultation**
    4. Choose your preferred date and time
    5. Confirm the booking

    ### 💡 Tips:
    - Book consultations at least 24 hours in advance
    - Prepare your questions and documents beforehand
    - Check the lawyer's fee range before booking
    """)

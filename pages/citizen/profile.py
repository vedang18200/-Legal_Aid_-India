import streamlit as st
from database.db_manager import execute_query
from config.settings import MAJOR_CITIES, SUPPORTED_LANGUAGES
from config.styles import apply_custom_styles

def show_profile_page():
    """Display user profile page"""
    apply_custom_styles()
    st.title("👤 My Profile")

    if not st.session_state.authenticated:
        st.warning("Please login to view profile")
        return

    try:
        # Get current user profile
        user_profile = execute_query(
            "SELECT username, email, phone, location, language FROM users WHERE id = %s",
            (st.session_state.user_id,), fetch='one'
        )

        if user_profile:
            username, email, phone, location, language = user_profile
        else:
            username = email = phone = location = language = ""

        render_profile_form(username, email, phone, location, language)

    except Exception as e:
        st.error(f"Error loading profile: {e}")

def render_profile_form(username, email, phone, location, language):
    """Render the profile update form"""
    with st.form("user_profile"):
        st.subheader("📝 Update Your Information")

        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("Username", value=username, disabled=True)
            new_email = st.text_input("Email", value=email or "")
            new_phone = st.text_input("Phone", value=phone or "")

        with col2:
            # Find current location index
            location_index = 0
            if location and location in MAJOR_CITIES:
                location_index = MAJOR_CITIES.index(location)

            new_location = st.selectbox("Location", MAJOR_CITIES, index=location_index)

            # Find current language index
            language_index = 0
            if language and language in SUPPORTED_LANGUAGES:
                language_index = SUPPORTED_LANGUAGES.index(language)

            new_language = st.selectbox("Preferred Language", SUPPORTED_LANGUAGES, index=language_index)

        address = st.text_area("Address", placeholder="Enter your full address")

        if st.form_submit_button("💾 Update Profile", type="primary"):
            handle_profile_update(new_email, new_phone, new_location, new_language)

def handle_profile_update(email, phone, location, language):
    """Handle profile update"""
    try:
        execute_query(
            "UPDATE users SET email = %s, phone = %s, location = %s, language = %s WHERE id = %s",
            (email, phone, location, language, st.session_state.user_id)
        )
        st.success("✅ Profile updated successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error updating profile: {e}")

def render_account_info():
    """Render account information section"""
    st.subheader("📊 Account Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Count user's cases
        case_count = execute_query(
            "SELECT COUNT(*) FROM cases WHERE user_id = %s",
            (st.session_state.user_id,), fetch='one'
        )
        st.metric("Total Cases", case_count[0] if case_count else 0)

    with col2:
        # Count consultations
        consultation_count = execute_query(
            "SELECT COUNT(*) FROM consultations WHERE user_id = %s",
            (st.session_state.user_id,), fetch='one'
        )
        st.metric("Consultations", consultation_count[0] if consultation_count else 0)

    with col3:
        # Account creation date
        creation_date = execute_query(
            "SELECT created_at FROM users WHERE id = %s",
            (st.session_state.user_id,), fetch='one'
        )
        if creation_date:
            st.metric("Member Since", creation_date[0].strftime("%Y-%m-%d"))

# ==========================================

# pages/lawyer/lawyer_profile.py
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
            # FIXED: Handle the correct number of columns from your database schema
            # Based on your lawyers table, the profile might return different columns
            # Let's use a safe unpacking approach

            if len(profile) == 8:
                # Original expected format
                name, email, phone, specialization, experience, location, languages, username = profile
                bar_registration = ""
                bio = ""
                fee_range = ""
                rating = None
                verified = False

            elif len(profile) >= 10:
                # Extended format - adjust based on what get_lawyer_profile actually returns
                # Check your services/lawyer_service.py to see the exact SELECT query
                try:
                    # Common approach: unpack what we know and handle extras safely
                    profile_data = list(profile)
                    name = profile_data[0] if len(profile_data) > 0 else ""
                    email = profile_data[1] if len(profile_data) > 1 else ""
                    phone = profile_data[2] if len(profile_data) > 2 else ""
                    specialization = profile_data[3] if len(profile_data) > 3 else ""
                    experience = profile_data[4] if len(profile_data) > 4 else 0
                    location = profile_data[5] if len(profile_data) > 5 else ""
                    languages = profile_data[6] if len(profile_data) > 6 else ""
                    username = profile_data[7] if len(profile_data) > 7 else ""
                    bar_registration = profile_data[8] if len(profile_data) > 8 else ""
                    bio = profile_data[9] if len(profile_data) > 9 else ""
                    fee_range = profile_data[10] if len(profile_data) > 10 else ""
                    rating = profile_data[11] if len(profile_data) > 11 else None
                    verified = profile_data[12] if len(profile_data) > 12 else False
                except Exception as e:
                    st.error(f"Error unpacking profile data: {e}")
                    st.info(f"Profile contains {len(profile)} fields: {profile}")
                    return
            else:
                st.error(f"Unexpected profile data format. Expected 8+ fields, got {len(profile)}")
                st.info(f"Profile data: {profile}")
                return
        else:
            # No profile found - set defaults
            name = email = phone = specialization = location = languages = ""
            experience = 0
            username = st.session_state.get('username', '')
            bar_registration = ""
            bio = ""
            fee_range = ""
            rating = None
            verified = False

        render_profile_form(name, email, phone, specialization, experience, location,
                          languages, username, bar_registration, bio, fee_range)

    except Exception as e:
        st.error(f"Error loading profile: {e}")
        st.info("Please check your database connection and lawyer_service.py")

def render_profile_form(name, email, phone, specialization, experience, location,
                       languages, username, bar_registration="", bio="", fee_range=""):
    """Render lawyer profile form with all fields"""
    with st.form("lawyer_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("Full Name", value=name or "")
            phone_input = st.text_input("Phone", value=phone or "")
            specialization_input = st.selectbox(
                "Specialization", LEGAL_CATEGORIES,
                index=LEGAL_CATEGORIES.index(specialization) if specialization in LEGAL_CATEGORIES else 0
            )
            languages_input = st.text_input("Languages", value=languages or "")
            fee_range_input = st.selectbox(
                "Fee Range (₹/hour)",
                ["500-1000", "1000-2000", "2000-5000", "5000-10000", "10000+"],
                index=0
            )

        with col2:
            experience_input = st.number_input(
                "Years of Experience", min_value=0, max_value=50, value=experience or 0
            )
            location_input = st.selectbox(
                "Location", MAJOR_CITIES,
                index=MAJOR_CITIES.index(location) if location in MAJOR_CITIES else 0
            )
            email_input = st.text_input("Email", value=email or "")
            bar_registration_input = st.text_input(
                "Bar Council Registration",
                value=bar_registration or "",
                placeholder="Registration Number"
            )

        bio_input = st.text_area(
            "Bio/Description",
            value=bio or "",
            placeholder="Brief description of your practice and expertise"
        )

        # ✅ Always render the button
        submitted = st.form_submit_button("Update Profile", type="primary")

        if submitted:
            try:
                success, message = update_lawyer_profile(
                    st.session_state.user_id,
                    full_name, email_input, phone_input,
                    specialization_input, experience_input,
                    location_input, languages_input
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"Error updating profile: {e}")

def show_profile_debug_info():
    """Debug function to check profile data structure"""
    if st.button("🔍 Debug Profile Data"):
        try:
            from database.db_manager import execute_query

            # Check what columns exist in lawyers table
            result = execute_query("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'lawyers'
                ORDER BY ordinal_position
            """, fetch='all')

            if result:
                st.write("**Lawyers table columns:**")
                for i, (col,) in enumerate(result):
                    st.write(f"{i+1}. {col}")

            # Check actual profile data
            profile_data = execute_query("""
                SELECT * FROM lawyers WHERE user_id = %s
            """, (st.session_state.user_id,), fetch='one')

            if profile_data:
                st.write(f"**Profile data ({len(profile_data)} columns):**")
                st.write(profile_data)
            else:
                st.write("No profile data found")

        except Exception as e:
            st.error(f"Debug error: {e}")

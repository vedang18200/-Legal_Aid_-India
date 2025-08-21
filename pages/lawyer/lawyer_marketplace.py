import streamlit as st
from services.lawyer_service import get_lawyers, get_lawyer_user_id
from config.settings import LEGAL_CATEGORIES, MAJOR_CITIES
from config.styles import apply_custom_styles
from database.db_manager import execute_query

def show_lawyer_marketplace():
    """Enhanced lawyer marketplace with better UI and debugging"""
    apply_custom_styles()

    st.title("👨‍⚖️ Lawyer Marketplace")
    st.markdown("Find and connect with verified legal professionals")

    # Debug section (can be removed in production)
    with st.expander("🔧 Debug Info", expanded=False):
        total_lawyers = execute_query("SELECT COUNT(*) FROM lawyers", fetch='one')
        verified_lawyers = execute_query("SELECT COUNT(*) FROM lawyers WHERE verified = true", fetch='one')
        st.write(f"Total lawyers in database: {total_lawyers[0] if total_lawyers else 0}")
        st.write(f"Verified lawyers: {verified_lawyers[0] if verified_lawyers else 0}")

    render_filters()
    render_search_bar()
    render_lawyers_list()

def render_search_bar():
    """Add search functionality"""
    st.markdown("### 🔍 Search Lawyers")
    search_term = st.text_input("Search by name, specialization, or location", key="lawyer_search")

    if search_term:
        st.session_state.search_term = search_term
    elif 'search_term' in st.session_state:
        del st.session_state.search_term

def render_filters():
    """Enhanced filter controls"""
    st.markdown("### 🔧 Filter Lawyers")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.session_state.specialization_filter = st.selectbox(
            "Specialization",
            ["All"] + LEGAL_CATEGORIES,
            key="lawyer_specialization_filter"
        )

    with col2:
        st.session_state.location_filter = st.selectbox(
            "Location",
            ["All"] + MAJOR_CITIES,
            key="lawyer_location_filter"
        )

    with col3:
        st.session_state.fee_filter = st.selectbox(
            "Fee Range",
            ["All", "₹0-500", "₹500-1500", "₹1500-3000", "₹3000+"],
            key="lawyer_fee_filter"
        )

    with col4:
        if st.button("🔄 Clear Filters", key="clear_filters"):
            clear_filters()

def clear_filters():
    """Clear all filters"""
    st.session_state.specialization_filter = "All"
    st.session_state.location_filter = "All"
    st.session_state.fee_filter = "All"
    if 'search_term' in st.session_state:
        del st.session_state.search_term
    st.rerun()

def render_lawyers_list():
    """Enhanced lawyers list with better error handling"""
    try:
        # Get filtered lawyers
        lawyers_df = get_lawyers(
            st.session_state.get('specialization_filter'),
            st.session_state.get('location_filter'),
            st.session_state.get('fee_filter')
        )

        if lawyers_df.empty:
            st.warning("🚫 No lawyers found matching your criteria.")
            st.info("💡 Try adjusting your filters or check back later for new lawyers.")
            return

        st.success(f"✅ Found {len(lawyers_df)} lawyer(s)")

        # Display lawyers in a grid-like layout
        for idx, lawyer in lawyers_df.iterrows():
            render_enhanced_lawyer_card(lawyer)
            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Error loading lawyers: {e}")
        st.info("Please try refreshing the page or contact support if the issue persists.")

def render_enhanced_lawyer_card(lawyer):
    """Enhanced lawyer card with better UI"""

    # Main card container
    with st.container():
        # Header row
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"""
            ### {lawyer['name']}
            **{lawyer['specialization']}**
            """)

        with col2:
            rating = lawyer.get('rating', 4.5)
            st.metric("Rating", f"⭐ {rating}/5.0")

        # Details row
        st.markdown(f"""
        **📍 Location:** {lawyer['location']} |
        **💼 Experience:** {lawyer['experience']} years |
        **💬 Languages:** {lawyer['languages']}
        """)

        if lawyer.get('fee_range'):
            st.markdown(f"**💰 Fee Range:** {lawyer['fee_range']}")

        # Action buttons
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button(f"📅 Book Consultation", key=f"book_{lawyer['id']}", type="primary"):
                handle_consultation_booking(lawyer)

        with col2:
            if st.button(f"👤 View Profile", key=f"profile_{lawyer['id']}"):
                handle_view_profile(lawyer)

        with col3:
            if st.button(f"💬 Start Chat", key=f"chat_{lawyer['id']}"):
                handle_lawyer_chat(lawyer)

        with col4:
            if st.button(f"📞 Contact Info", key=f"contact_{lawyer['id']}"):
                handle_contact_info(lawyer)

def handle_consultation_booking(lawyer):
    """Enhanced consultation booking"""
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Please login to book consultation")
        return

    # Store booking info in session state for the booking form
    st.session_state.booking_lawyer = lawyer
    st.session_state.show_booking_form = True

    # Show success message
    st.success(f"✅ Opening booking form for {lawyer['name']}")
    st.info("💡 A booking form will appear. Please fill in your preferred date and time.")

def handle_view_profile(lawyer):
    """Handle viewing lawyer profile"""
    with st.expander(f"👤 {lawyer['name']}'s Profile", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **📧 Email:** {lawyer.get('email', 'Not provided')}
            **📱 Phone:** {lawyer.get('phone', 'Not provided')}
            **🎓 Experience:** {lawyer['experience']} years
            **📍 Location:** {lawyer['location']}
            """)

        with col2:
            st.markdown(f"""
            **⚖️ Specialization:** {lawyer['specialization']}
            **🗣️ Languages:** {lawyer['languages']}
            **💰 Fee Range:** {lawyer.get('fee_range', 'Contact for details')}
            **⭐ Rating:** {lawyer.get('rating', 4.5)}/5.0
            """)

def handle_lawyer_chat(lawyer):
    """Enhanced chat initiation"""
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Please login to start chat")
        return

    try:
        # Find lawyer's user_id
        lawyer_user_id = get_lawyer_user_id(lawyer['id'])

        if lawyer_user_id:
            # Set chat session data
            st.session_state.chat_with = lawyer_user_id
            st.session_state.chat_with_name = lawyer['name']
            st.session_state.current_page = "Messages"

            # Create initial chat record if needed
            create_initial_chat_record(lawyer_user_id, lawyer['name'])

            st.success(f"✅ Starting chat with {lawyer['name']}")
            st.info("🔄 Redirecting to messages...")

            # Add a small delay before redirect
            import time
            time.sleep(1)
            st.rerun()

        else:
            st.error("❌ Unable to start chat with this lawyer. Please try again.")

    except Exception as e:
        st.error(f"❌ Error starting chat: {e}")

def handle_contact_info(lawyer):
    """Show contact information"""
    with st.expander(f"📞 Contact {lawyer['name']}", expanded=True):
        st.markdown(f"""
        ### Contact Information

        **📧 Email:** {lawyer.get('email', 'Not provided')}

        **📱 Phone:** {lawyer.get('phone', 'Not provided')}

        **📍 Office Location:** {lawyer['location']}

        **💼 Specialization:** {lawyer['specialization']}

        ---

        **💡 Quick Actions:**
        - Use the **Start Chat** button for instant messaging
        - Use the **Book Consultation** button to schedule a meeting
        - Contact directly using the phone/email above
        """)

def create_initial_chat_record(lawyer_user_id, lawyer_name):
    """Create initial chat record between user and lawyer"""
    try:
        current_user_id = st.session_state.get('user_id')
        if not current_user_id:
            return

        # Check if chat already exists
        existing_chat = execute_query(
            """SELECT id FROM messages
               WHERE (sender_id = %s AND receiver_id = %s)
               OR (sender_id = %s AND receiver_id = %s)""",
            (current_user_id, lawyer_user_id, lawyer_user_id, current_user_id),
            fetch='one'
        )

        if not existing_chat:
            # Create initial message
            execute_query(
                """INSERT INTO messages (sender_id, receiver_id, content, created_at, read_status)
                   VALUES (%s, %s, %s, NOW(), false)""",
                (current_user_id, lawyer_user_id, f"Hi {lawyer_name}, I'm interested in your legal services. Could you please help me?")
            )

    except Exception as e:
        st.error(f"Error creating initial chat: {e}")

# Booking form component
def show_booking_form():
    """Show consultation booking form"""
    if not st.session_state.get('show_booking_form', False):
        return

    lawyer = st.session_state.get('booking_lawyer')
    if not lawyer:
        return

    st.markdown("### 📅 Book Consultation")

    with st.form(key="booking_form"):
        st.markdown(f"**Booking consultation with: {lawyer['name']}**")

        col1, col2 = st.columns(2)

        with col1:
            preferred_date = st.date_input("Preferred Date")
            case_type = st.selectbox(
                "Type of Case",
                ["Civil", "Criminal", "Corporate", "Family", "Property", "Other"]
            )

        with col2:
            preferred_time = st.time_input("Preferred Time")
            urgency = st.selectbox(
                "Urgency Level",
                ["Low", "Medium", "High", "Emergency"]
            )

        case_description = st.text_area("Brief Description of Your Case")
        contact_preference = st.selectbox(
            "Preferred Contact Method",
            ["Phone", "Email", "Video Call", "In-Person"]
        )

        # Submit button - THIS IS IMPORTANT!
        submitted = st.form_submit_button("📅 Submit Booking Request")

        if submitted:
            # Process the booking
            success = process_booking_request(
                lawyer, preferred_date, preferred_time,
                case_type, urgency, case_description, contact_preference
            )

            if success:
                st.success(f"✅ Booking request sent to {lawyer['name']}!")
                st.info("📧 You will receive a confirmation email shortly.")
                # Clear the booking form
                st.session_state.show_booking_form = False
                st.session_state.booking_lawyer = None
                st.rerun()
            else:
                st.error("❌ Failed to submit booking request. Please try again.")

def process_booking_request(lawyer, preferred_date, preferred_time, case_type, urgency, description, contact_preference):
    """Process the booking request"""
    try:
        current_user_id = st.session_state.get('user_id')
        if not current_user_id:
            return False

        # Insert booking request into database
        execute_query(
            """INSERT INTO consultation_bookings
               (client_id, lawyer_id, preferred_date, preferred_time,
                case_type, urgency, description, contact_preference,
                status, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (current_user_id, lawyer['id'], preferred_date, preferred_time,
             case_type, urgency, description, contact_preference, 'pending')
        )

        return True

    except Exception as e:
        st.error(f"Database error: {e}")
        return False

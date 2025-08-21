import streamlit as st
from services.case_service import create_case, get_user_cases
from config.settings import LEGAL_CATEGORIES, CASE_PRIORITIES
from config.styles import apply_custom_styles, STATUS_COLORS

def show_case_tracking():
    """Display case tracking and management page"""
    apply_custom_styles()
    st.title("📋 Case Tracking & Management")

    if not st.session_state.authenticated:
        st.warning("Please login to access case tracking")
        return

    render_new_case_form()
    render_existing_cases()

def render_new_case_form():
    """Render form to create new case"""
    with st.expander("➕ Add New Case"):
        with st.form("new_case_form"):
            case_title = st.text_input("Case Title")
            case_description = st.text_area("Case Description")
            case_category = st.selectbox("Category", LEGAL_CATEGORIES)
            case_priority = st.selectbox("Priority", CASE_PRIORITIES)

            if st.form_submit_button("Create Case"):
                success, message = create_case(
                    st.session_state.user_id,
                    case_title,
                    case_description,
                    case_category,
                    case_priority
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def render_existing_cases():
    """Render existing cases for the user"""
    try:
        cases = get_user_cases(st.session_state.user_id)

        if not cases:
            st.info("No cases found. Create your first case above.")
            return

        st.subheader("My Cases")

        for case in cases:
            render_case_card(case)

    except Exception as e:
        st.error(f"Error loading cases: {e}")

def render_case_card(case):
    """Render individual case card"""
    # Handle the case as a tuple/list - access by index to avoid unpacking errors
    case_id = case[0]
    user_id = case[1]
    lawyer_id = case[2] if len(case) > 2 else None
    title = case[3] if len(case) > 3 else "No Title"
    description = case[4] if len(case) > 4 else "No Description"
    category = case[5] if len(case) > 5 else "Unknown"
    status = case[6] if len(case) > 6 else "Pending"
    priority = case[7] if len(case) > 7 else "Low"
    created_at = case[8] if len(case) > 8 else "Unknown"
    updated_at = case[9] if len(case) > 9 else None
    lawyer_name = case[10] if len(case) > 10 else None

    status_class = f"status-{status.lower().replace(' ', '-')}" if status else "status-pending"

    st.markdown(f"""
    <div class="feature-card">
        <h4>{title} <span class="case-status {status_class}">{status or 'Pending'}</span></h4>
        <p><strong>Category:</strong> {category} | <strong>Priority:</strong> {priority}</p>
        <p><strong>Description:</strong> {description}</p>
        <p><strong>Lawyer:</strong> {lawyer_name or 'Not assigned'}</p>
        <p><strong>Created:</strong> {created_at}</p>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"Update Status", key=f"update_{case_id}"):
            st.info("Status update feature - to be implemented")
    with col2:
        if st.button(f"Upload Documents", key=f"docs_{case_id}"):
            st.info("Document upload feature - to be implemented")
    with col3:
        if lawyer_id and st.button(f"Contact Lawyer", key=f"contact_lawyer_{case_id}"):
            st.session_state.chat_with = lawyer_id
            st.session_state.chat_with_name = lawyer_name
            st.session_state.current_page = "Messages"
            st.rerun()

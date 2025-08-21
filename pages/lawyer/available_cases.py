import streamlit as st
from services.case_service import get_available_cases, assign_case_to_lawyer
from config.styles import apply_custom_styles, PRIORITY_COLORS
from database.db_manager import execute_query

def show_available_cases():
    """Display available cases for lawyers"""
    apply_custom_styles()
    st.title("💼 Available Cases")

    if not st.session_state.authenticated or st.session_state.user_type != "Lawyer":
        st.warning("This page is only for lawyers")
        return

    try:
        cases = get_available_cases()

        if not cases:
            st.info("No available cases at the moment.")
            return

        st.write(f"Found {len(cases)} available cases")

        for case in cases:
            render_available_case_card(case)

    except Exception as e:
        st.error(f"Error loading available cases: {e}")

def render_available_case_card(case):
    """Render individual available case card"""
    case_id, title, description, category, priority, created_at, client_name, location = case

    # Priority colors
    priority_color = PRIORITY_COLORS.get(priority, '#6c757d')

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #f8f9fa;">
        <h4>{title} <span style="background-color: {priority_color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{priority}</span></h4>
        <p><strong>Client:</strong> {client_name} | <strong>Category:</strong> {category} | <strong>Location:</strong> {location}</p>
        <p><strong>Description:</strong> {description}</p>
        <p><small><strong>Created:</strong> {created_at}</small></p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"Take Case", key=f"take_{case_id}"):
            handle_take_case(case_id)

    with col2:
        if st.button(f"View Details", key=f"details_{case_id}"):
            st.info(f"Detailed view for case #{case_id}")

    with col3:
        if st.button(f"Contact Client", key=f"contact_{case_id}"):
            handle_contact_client(case_id, client_name)

def handle_take_case(case_id):
    """Handle taking a case"""
    success, message = assign_case_to_lawyer(case_id, st.session_state.user_id)
    if success:
        st.success(message)
        st.rerun()
    else:
        st.error(message)

def handle_contact_client(case_id, client_name):
    """Handle contacting client"""
    # Get client's user_id for messaging
    client_user = execute_query(
        "SELECT user_id FROM cases WHERE id = %s",
        (case_id,),
        fetch='one'
    )
    if client_user:
        st.session_state.chat_with = client_user[0]
        st.session_state.chat_with_name = client_name
        st.session_state.current_page = "Messages"
        st.rerun()
    else:
        st.error("Unable to contact client")    

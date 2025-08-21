import streamlit as st
from utils.session_manager import get_navigation_menu, logout_user, demo_login
from utils.auth_manager import authenticate_user
from config.settings import APP_SETTINGS

def render_sidebar():
    """Render the sidebar navigation and authentication"""
    st.sidebar.title("⚖️ Legal Aid India")

    if st.session_state.authenticated:
        render_authenticated_sidebar()
    else:
        render_guest_sidebar()

    st.sidebar.markdown("---")
    render_navigation()
    st.sidebar.markdown("---")
    render_help_section()

def render_authenticated_sidebar():
    """Render sidebar for authenticated users"""
    user_type = st.session_state.get('user_type', 'Citizen')
    st.sidebar.success(f"✅ Welcome!\n**User:** {st.session_state.get('username', 'User')}\n**Type:** {user_type}")

    if st.sidebar.button("🚪 Logout", use_container_width=True, type="primary"):
        logout_user()
        st.success("👋 Logged out successfully!")
        st.rerun()

def render_guest_sidebar():
    """Render sidebar for guest users"""
    st.sidebar.info("👤 **Not logged in**\nSome features require authentication")

    # Quick login widget in sidebar
    with st.sidebar.expander("🔐 Quick Login"):
        quick_username = st.text_input("Username", key="sidebar_username", placeholder="Your username")
        quick_password = st.text_input("Password", type="password", key="sidebar_password", placeholder="Your password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="sidebar_login", use_container_width=True):
                if quick_username and quick_password:
                    result = authenticate_user(quick_username, quick_password)
                    if result:
                        st.session_state.authenticated = True
                        st.session_state.user_id = result[0]
                        st.session_state.user_type = result[1]
                        st.session_state.username = quick_username
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.warning("⚠️ Enter credentials")

        with col2:
            if st.button("Demo", key="sidebar_demo", use_container_width=True):
                demo_login()
                st.success("✅ Demo mode!")
                st.rerun()

def render_navigation():
    """Render navigation menu"""
    pages = get_navigation_menu()

    # Use radio buttons for navigation
    current_index = 0
    if st.session_state.current_page in pages.values():
        current_index = list(pages.values()).index(st.session_state.current_page)

    selected_page = st.sidebar.radio(
        "🧭 Navigate to:",
        list(pages.keys()),
        index=current_index,
        key="main_navigation"
    )

    # Update current page when selection changes
    new_page = pages[selected_page]
    if new_page != st.session_state.current_page:
        st.session_state.current_page = new_page
        st.rerun()

def render_help_section():
    """Render help section based on user type"""
    user_type = st.session_state.get('user_type', 'Guest')

    if user_type == "Citizen":
        st.sidebar.markdown("### 🆘 Quick Help")
        st.sidebar.markdown(f"""
        - **Emergency Legal Helpline**: {APP_SETTINGS['emergency_helpline']}
        - **NALSA Helpline**: {APP_SETTINGS['nalsa_helpline']}
        - **Women Helpline**: {APP_SETTINGS['women_helpline']}
        - **Cyber Crime**: {APP_SETTINGS['cyber_crime_helpline']}
        """)
    elif user_type == "Lawyer":
        st.sidebar.markdown("### 💼 Lawyer Resources")
        st.sidebar.markdown("""
        - **Bar Council**: 1800-XXX-XXXX
        - **Legal Updates**: Check notifications
        - **Client Support**: 24/7 available
        - **Technical Help**: support@legal.com
        """)
    else:
        st.sidebar.markdown("### 🆘 General Help")
        st.sidebar.markdown(f"""
        - **Emergency Legal Helpline**: {APP_SETTINGS['emergency_helpline']}
        - **Support**: support@legal.com
        """)

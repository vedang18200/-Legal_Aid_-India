import streamlit as st
from utils.auth_manager import authenticate_user, register_user, validate_registration_data, hash_password
from utils.session_manager import demo_login
from config.settings import MAJOR_CITIES, SUPPORTED_LANGUAGES, USER_TYPES
from database.db_manager import execute_query

def show_login_page():
    """Display login and registration page"""
    st.title("🔐 Login / Register")

    if st.button("← Back to Home"):
        st.session_state.current_page = "Home"
        st.rerun()

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        render_login_form()

    with tab2:
        render_registration_form()

def render_login_form():
    """Render the login form"""
    st.subheader("Welcome Back!")
    st.write("Please enter your credentials to access your account.")

    debug_mode = st.checkbox("🐛 Debug Mode (Show technical details)")

    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

        col1, col2, col3 = st.columns(3)
        with col1:
            login_button = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        with col2:
            demo_button = st.form_submit_button("🎯 Demo Login", use_container_width=True)
        with col3:
            test_button = st.form_submit_button("🔍 Test User", use_container_width=True)

        if login_button:
            handle_login(username, password, debug_mode)
        elif demo_button:
            handle_demo_login()
        elif test_button:
            show_test_users()

    st.markdown("---")
    st.info("💡 **Demo Access**: Click 'Demo Login' to explore the platform without creating an account.")

def handle_login(username, password, debug_mode):
    """Handle user login"""
    if username and password:
        if debug_mode:
            st.info(f"Attempting to login user: '{username}'")

        result = authenticate_user(username, password)
        if result:
            st.session_state.authenticated = True
            st.session_state.user_id = result[0]
            st.session_state.user_type = result[1]
            st.session_state.username = username
            st.success("✅ Login successful! Redirecting...")
            st.session_state.current_page = "Home"
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")
            if debug_mode:
                all_users = execute_query("SELECT username FROM users LIMIT 5", fetch='all')
                if all_users:
                    st.write("Debug: Available users:", [user[0] for user in all_users])
    else:
        st.warning("⚠️ Please enter both username and password.")

def handle_demo_login():
    """Handle demo login"""
    demo_login()
    st.success("✅ Demo login successful! Welcome to the demo!")
    st.session_state.current_page = "Home"
    st.rerun()

def show_test_users():
    """Show available test users for debugging"""
    test_users = execute_query("SELECT username FROM users LIMIT 3", fetch='all')
    if test_users:
        st.info(f"Available test users: {[user[0] for user in test_users]}")
    else:
        st.warning("No users found in database")

def render_registration_form():
    """Render the registration form"""
    st.subheader("Create New Account")
    st.write("Join our platform to access legal aid services.")

    with st.form("register_form"):
        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input("👤 Choose Username", placeholder="Enter desired username")
            new_password = st.text_input("🔒 Choose Password", type="password", placeholder="Minimum 6 characters")
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            phone = st.text_input("📱 Phone Number", placeholder="+91-XXXXXXXXXX")

        with col2:
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password")
            location = st.selectbox("📍 Location", MAJOR_CITIES)
            language = st.selectbox("🗣️ Preferred Language", SUPPORTED_LANGUAGES)
            user_type = st.selectbox("👥 Account Type", USER_TYPES)

        register_button = st.form_submit_button("🎉 Create Account", use_container_width=True, type="primary")

        if register_button:
            handle_registration(new_username, new_password, confirm_password, email, phone, location, language, user_type)

    st.markdown("---")
    st.info("📋 **Account Types**:\n- **Citizen**: Access legal aid services\n- **Lawyer**: Provide legal services\n- **Legal Aid Worker**: Manage and coordinate services")

def handle_registration(username, password, confirm_password, email, phone, location, language, user_type):
    """Handle user registration"""
    errors = validate_registration_data(username, password, confirm_password, email, phone)

    if errors:
        for error in errors:
            st.error(f"❌ {error}")
        return

    success, message = register_user(username, password, email, phone, location, language, user_type)

    if success:
        st.success("🎉 " + message)
        st.info(f"✅ You can now login with username: '{username}'")
        st.balloons()

        if st.checkbox("Show debug info"):
            st.code(f"Username: {username}")
            st.code(f"Password hash: {hash_password(password)}")
    else:
        st.error("❌ " + message)

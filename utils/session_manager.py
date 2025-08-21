import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chat_with' not in st.session_state:
        st.session_state.chat_with = None
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False

def logout_user():
    """Clear session state and logout user"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.user_type = None
    st.session_state.username = None
    st.session_state.chat_history = []
    st.session_state.chat_with = None
    st.session_state.chat_open = False
    st.session_state.current_page = "Home"

def demo_login():
    """Set demo user session"""
    st.session_state.authenticated = True
    st.session_state.user_id = 999
    st.session_state.user_type = "Citizen"
    st.session_state.username = "Demo User"

def get_navigation_menu():
    """Return navigation menu based on user type"""
    if not st.session_state.authenticated:
        # Public/Guest navigation
        return {
            "🏠 Home": "Home",
            "🤖 Legal Chatbot": "Chatbot",
            "👨‍⚖️ Find Lawyers": "Lawyers",
            "📖 Legal Awareness": "Awareness",
            "🔐 Login / Register": "Login"
        }

    user_type = st.session_state.get('user_type', 'Citizen')

    if user_type == "Citizen":
        return {
            "🏠 Home": "Home",
            "🤖 Legal Chatbot": "Chatbot",
            "👨‍⚖️ Find Lawyers": "Lawyers",
            "📋 My Cases": "Cases",
            "📅 Consultations": "Consultations",
            "📖 Legal Awareness": "Awareness",
            "💬 Messages": "Messages",
            "👤 Profile": "Profile"
        }

    elif user_type == "Lawyer":
        return {
            "🏠 Dashboard": "LawyerDashboard",
            "💼 Available Cases": "AvailableCases",
            "📋 My Cases": "LawyerCases",
            "👥 My Clients": "LawyerClients",
            "📅 Appointments": "LawyerAppointments",
            "💬 Messages": "Messages",
            "💰 Earnings": "LawyerEarnings",
            "⚖️ Legal Resources": "LawyerResources",
            "👤 Profile": "LawyerProfile"
        }

    elif user_type == "Legal Aid Worker":
        return {
            "🏠 Admin Dashboard": "AdminDashboard",
            "📊 Case Management": "AdminCases",
            "👨‍⚖️ Lawyer Management": "AdminLawyers",
            "👥 User Management": "AdminUsers",
            "📈 Analytics": "AdminAnalytics",
            "⚙️ Settings": "AdminSettings"
        }

    else:
        return {
            "🏠 Home": "Home",
            "🤖 Legal Chatbot": "Chatbot",
            "📖 Legal Awareness": "Awareness"
        }

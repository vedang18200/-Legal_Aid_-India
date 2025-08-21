import streamlit as st

def show_admin_pages(page_name):
    """Show admin pages based on page name"""
    if page_name == "AdminDashboard":
        show_admin_dashboard()
    elif page_name == "AdminCases":
        show_admin_cases()
    elif page_name == "AdminLawyers":
        show_admin_lawyers()
    elif page_name == "AdminUsers":
        show_admin_users()
    elif page_name == "AdminAnalytics":
        show_admin_analytics()
    elif page_name == "AdminSettings":
        show_admin_settings()
    else:
        st.error(f"Admin page not found: {page_name}")

def show_admin_dashboard():
    """Display main admin dashboard"""
    st.title("🏠 Admin Dashboard")
    st.info("📊 Admin dashboard features coming soon!")

    # Placeholder metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", "1,234", "5%")
    with col2:
        st.metric("Active Cases", "567", "12%")
    with col3:
        st.metric("Verified Lawyers", "89", "3%")
    with col4:
        st.metric("Resolved Cases", "890", "8%")

def show_admin_cases():
    """Display case management for admins"""
    st.title("📊 Case Management")
    st.info("🔧 Admin case management features coming soon!")

def show_admin_lawyers():
    """Display lawyer management for admins"""
    st.title("👨‍⚖️ Lawyer Management")
    st.info("🔧 Lawyer verification and management features coming soon!")

def show_admin_users():
    """Display user management for admins"""
    st.title("👥 User Management")
    st.info("🔧 User management features coming soon!")

def show_admin_analytics():
    """Display analytics for admins"""
    st.title("📈 Analytics")
    st.info("📊 Analytics and reporting features coming soon!")

def show_admin_settings():
    """Display admin settings"""
    st.title("⚙️ Settings")
    st.info("⚙️ System settings and configuration coming soon!")

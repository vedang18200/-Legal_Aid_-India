
# ==========================================

# pages/lawyer/earnings.py
import streamlit as st
from config.styles import apply_custom_styles

def show_lawyer_earnings():
    """Display lawyer earnings page"""
    apply_custom_styles()
    st.title("💰 Earnings Dashboard")
    st.info("📊 Earnings tracking and analytics features coming soon!")

    # Placeholder earnings display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("This Month", "₹25,000", "12%")
    with col2:
        st.metric("Last Month", "₹22,300", "-5%")
    with col3:
        st.metric("Total Earnings", "₹2,45,000")
    with col4:
        st.metric("Pending Payments", "₹8,500")



# import streamlit as st
# from config.styles import apply_custom_styles

# def show_lawyer_earnings():
#     """Display lawyer earnings page"""
#     apply_custom_styles()
#     st.title("💰 Earnings Dashboard")
#     st.info("📊 Earnings tracking and analytics features coming soon!")

#     # Placeholder earnings display
#     col1, col2, col3, col4 = st.columns(4)
#     with col1:
#         st.metric("This Month", "₹25,000", "12%")
#     with col2:
#         st.metric("Last Month", "₹22,300", "-5%")
#     with col3:
#         st.metric("Total Earnings", "₹2,45,000")
#     with col4:
#         st.metric("Pending Payments", "₹8,500")

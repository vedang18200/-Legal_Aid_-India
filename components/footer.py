import streamlit as st
from config.settings import APP_SETTINGS

def render_footer():
    """Render the application footer"""
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Legal Aid India Platform | Empowering Justice for All</p>
        <p>For emergency legal assistance, contact: <strong>Emergency Legal Helpline: {APP_SETTINGS['emergency_helpline']}</strong></p>
    </div>
    """, unsafe_allow_html=True)

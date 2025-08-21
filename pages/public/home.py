import streamlit as st
from config.styles import apply_custom_styles

def show_home_page():
    """Display the home page"""
    apply_custom_styles()

    st.markdown('''
    <div class="main-header">
        <h1>⚖️ Legal Aid India</h1>
        <p>Bridging the Justice Gap - Free & Affordable Legal Services</p>
    </div>
    ''', unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="feature-card">
                <h3>🤖 Legal Chatbot</h3>
                <p>Get instant answers to basic legal queries in your preferred language</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Try Chatbot", key="home_chatbot"):
            st.session_state.current_page = "Chatbot"
            st.rerun()

    with col2:
        st.markdown("""
            <div class="feature-card">
                <h3>👨‍⚖️ Find Lawyers</h3>
                <p>Connect with verified lawyers for consultation and representation</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Find Lawyers", key="home_lawyers"):
            st.session_state.current_page = "Lawyers"
            st.rerun()

    with col3:
        st.markdown("""
            <div class="feature-card">
                <h3>📋 Track Cases</h3>
                <p>Monitor your case progress and important deadlines</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Track Cases", key="home_cases"):
            st.session_state.current_page = "Cases"
            st.rerun()

    st.markdown("---")

    # Quick stats
    render_stats()

def render_stats():
    """Render platform statistics"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Registered Lawyers", "150+")
    with col2:
        st.metric("Cases Resolved", "1,200+")
    with col3:
        st.metric("Users Helped", "5,000+")
    with col4:
        st.metric("Languages Supported", "10+")

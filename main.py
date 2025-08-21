import streamlit as st
from config.settings import configure_page
from database.db_manager import init_database, init_sample_data
from utils.session_manager import init_session_state
from components.sidebar import render_sidebar
from router import route_to_page
from components.footer import render_footer

def main():
    """Main application entry point"""
    # Configure page
    configure_page()

    # Initialize database and session
    init_database()
    init_session_state()
    init_sample_data()

    # Render sidebar navigation
    render_sidebar()

    # Route to appropriate page
    route_to_page()

    # Render footer
    render_footer()

if __name__ == "__main__":
    main()

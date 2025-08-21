
# ==========================================

# pages/lawyer/resources.py
import streamlit as st
from config.styles import apply_custom_styles

def show_lawyer_resources():
    """Display lawyer resources page"""
    apply_custom_styles()
    st.title("⚖️ Legal Resources")
    st.info("📚 Legal resources and reference materials coming soon!")

    # Placeholder content
    with st.expander("📖 Case Law Database"):
        st.markdown("Access to latest case laws and judgments")

    with st.expander("📋 Legal Forms & Templates"):
        st.markdown("Downloadable legal forms and document templates")

    with st.expander("📰 Legal News & Updates"):
        st.markdown("Latest legal news and regulatory updates")


# # ===========================================
# # FILE: pages/lawyer/resources.py
# # ===========================================

# import streamlit as st
# from config.styles import apply_custom_styles

# def show_lawyer_resources():
#     """Display lawyer resources page"""
#     apply_custom_styles()
#     st.title("⚖️ Legal Resources")
#     st.info("📚 Legal resources and reference materials coming soon!")

#     # Placeholder content
#     with st.expander("📖 Case Law Database"):
#         st.markdown("Access to latest case laws and judgments")

#     with st.expander("📋 Legal Forms & Templates"):
#         st.markdown("Downloadable legal forms and document templates")

#     with st.expander("📰 Legal News & Updates"):
#         st.markdown("Latest legal news and regulatory updates")

import streamlit as st
from services.chatbot_service import get_legal_response, save_chat_message, get_quick_questions
from config.settings import SUPPORTED_LANGUAGES
from config.styles import apply_custom_styles

def show_chatbot_page():
    """Display the legal chatbot page"""
    apply_custom_styles()
    st.title("🤖 Legal Assistant Chatbot")

    col1, col2 = st.columns([2, 1])

    with col2:
        render_chatbot_controls()

    with col1:
        render_chat_interface()

def render_chatbot_controls():
    """Render chatbot control panel"""
    language = st.selectbox("Select Language", SUPPORTED_LANGUAGES)

    st.markdown("### Quick Questions:")
    quick_questions = get_quick_questions()

    for question in quick_questions:
        if st.button(question, key=f"quick_{question}"):
            st.session_state.chat_history.append(("user", question))
            response = get_legal_response(question, language)
            st.session_state.chat_history.append(("bot", response))
            st.rerun()

def render_chat_interface():
    """Render the main chat interface"""
    st.markdown("### Chat with Legal Assistant")

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for sender, message in st.session_state.chat_history[-10:]:
            if sender == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message"><strong>Legal Assistant:</strong> {message}</div>', unsafe_allow_html=True)

    # Chat input
    user_input = st.text_input("Ask your legal question:", placeholder="Type your question here...")

    if st.button("Send") and user_input:
        language = st.selectbox("Language", SUPPORTED_LANGUAGES, key="chat_lang", label_visibility="collapsed")

        st.session_state.chat_history.append(("user", user_input))
        response = get_legal_response(user_input, language)
        st.session_state.chat_history.append(("bot", response))

        # Save to database if user is logged in
        if st.session_state.authenticated:
            save_chat_message(st.session_state.user_id, user_input, response, language)

        st.rerun()

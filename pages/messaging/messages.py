import streamlit as st
from services.messaging_service import (
    get_user_conversations, get_messages, send_message,
    create_appointment_request, get_user_appointments,
    get_conversation_stats, is_user_blocked
)
from config.styles import apply_custom_styles
from datetime import datetime, timedelta

def show_messages_page():
    """Enhanced messages page with better GUI and appointment integration"""
    apply_custom_styles()

    # Initialize blocked_users table if it doesn't exist
    initialize_blocked_users_table()

    # Custom CSS for better chat appearance
    st.markdown("""
    <style>
    .chat-container {
        height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        background-color: #f9f9f9;
    }
    .message-sent {
        background-color: #007bff;
        color: white;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px 0;
        text-align: right;
        margin-left: 20%;
    }
    .message-received {
        background-color: #e9ecef;
        color: black;
        padding: 8px 12px;
        border-radius: 15px;
        margin: 5px 0;
        margin-right: 20%;
    }
    .conversation-item {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        cursor: pointer;
    }
    .conversation-item:hover {
        background-color: #f0f0f0;
    }
    .unread-badge {
        background-color: #dc3545;
        color: white;
        border-radius: 50%;
        padding: 2px 6px;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("💬 Messages")

    if not st.session_state.get('authenticated', False):
        st.warning("Please login to access messages")
        return

    # Show conversation stats
    show_conversation_stats()

    # Main layout
    col1, col2 = st.columns([1, 2])

    with col1:
        render_enhanced_conversations_list()

    with col2:
        if st.session_state.get('chat_with'):
            render_enhanced_chat_interface()
        else:
            show_welcome_message()

def initialize_blocked_users_table():
    """Initialize blocked_users table if it doesn't exist"""
    try:
        from database.db_manager import execute_query

        # Check if table exists, if not create it
        execute_query("""
            CREATE TABLE IF NOT EXISTS public.blocked_users (
                id SERIAL NOT NULL,
                blocker_id INTEGER NULL,
                blocked_id INTEGER NULL,
                blocked_at TIMESTAMP WITHOUT TIME ZONE NULL DEFAULT CURRENT_TIMESTAMP,
                reason TEXT NULL,
                CONSTRAINT blocked_users_pkey PRIMARY KEY (id),
                CONSTRAINT blocked_users_blocker_id_fkey FOREIGN KEY (blocker_id) REFERENCES users (id) ON DELETE CASCADE,
                CONSTRAINT blocked_users_blocked_id_fkey FOREIGN KEY (blocked_id) REFERENCES users (id) ON DELETE CASCADE,
                CONSTRAINT unique_blocked_pair UNIQUE (blocker_id, blocked_id)
            )
        """, fetch=False)

        # Create indexes
        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_blocked_users_blocker
            ON public.blocked_users USING btree (blocker_id)
        """, fetch=False)

        execute_query("""
            CREATE INDEX IF NOT EXISTS idx_blocked_users_blocked
            ON public.blocked_users USING btree (blocked_id)
        """, fetch=False)

    except Exception as e:
        st.error(f"Error initializing blocked_users table: {e}")

def show_conversation_stats():
    """Show conversation statistics"""
    user_id = st.session_state.get('user_id')
    if user_id:
        try:
            total_convs, total_msgs, unread_msgs = get_conversation_stats(user_id)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Conversations", total_convs)
            with col2:
                st.metric("Total Messages", total_msgs)
            with col3:
                st.metric("Unread Messages", unread_msgs, delta=unread_msgs if unread_msgs > 0 else None)
        except Exception as e:
            st.error(f"Error loading conversation stats: {e}")

def render_enhanced_conversations_list():
    """Enhanced conversations list with better UI"""
    st.markdown("### 📨 Conversations")

    # Search conversations
    search_term = st.text_input("🔍 Search conversations", key="conv_search")

    try:
        conversations = get_user_conversations(st.session_state.user_id)

        if conversations:
            for conv in conversations:
                other_user_id, other_username, other_user_type, last_message_time, last_message, unread_count = conv

                # Filter by search term if provided
                if search_term and search_term.lower() not in other_username.lower():
                    continue

                # Create conversation card
                with st.container():
                    # Conversation header
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        user_display = f"{other_username}"
                        if other_user_type:
                            user_display += f" ({other_user_type.title()})"

                        if st.button(
                            user_display,
                            key=f"conv_{other_user_id}",
                            use_container_width=True
                        ):
                            st.session_state.chat_with = other_user_id
                            st.session_state.chat_with_name = other_username
                            st.session_state.chat_with_type = other_user_type
                            st.rerun()

                    with col2:
                        if unread_count > 0:
                            st.markdown(f'<span class="unread-badge">{unread_count}</span>',
                                      unsafe_allow_html=True)

                    # Last message preview
                    if last_message:
                        preview = last_message[:40] + "..." if len(last_message) > 40 else last_message
                        st.caption(f"💬 {preview}")

                    # Timestamp
                    if last_message_time:
                        st.caption(f"🕒 {format_timestamp(last_message_time)}")

                    st.markdown("---")
        else:
            st.info("🔭 No conversations yet. Start messaging from the lawyers marketplace!")
            if st.button("🔍 Find Lawyers"):
                st.session_state.current_page = "Lawyer Marketplace"
                st.rerun()
    except Exception as e:
        st.error(f"Error loading conversations: {e}")

def show_welcome_message():
    """Show welcome message when no chat is selected"""
    st.markdown("""
    ### 👋 Welcome to Messages!

    Select a conversation from the left to start chatting.

    **Quick Tips:**
    - 📅 Use the appointment button to schedule meetings
    - 🔍 Search through your conversations
    - 📎 Send important documents (coming soon)
    - 📞 Voice/Video calls (coming soon)
    """)

def render_enhanced_chat_interface():
    """Enhanced chat interface with appointment scheduling"""
    chat_with_id = st.session_state.chat_with
    chat_with_name = st.session_state.get('chat_with_name', 'User')
    chat_with_type = st.session_state.get('chat_with_type', '')

    # Chat header
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.markdown(f"### 💬 {chat_with_name}")
        if chat_with_type:
            st.caption(f"Role: {chat_with_type.title()}")

    with col2:
        if st.button("📅 Schedule Meeting", key="schedule_btn"):
            st.session_state.show_appointment_form = True
            st.rerun()

    with col3:
        if st.button("📞 Call", key="call_btn"):
            st.info("📞 Voice/Video calling feature coming soon!")

    with col4:
        if st.button("ℹ️ Info", key="info_btn"):
            show_user_info(chat_with_id)

    # Show appointment form if requested
    if st.session_state.get('show_appointment_form', False):
        show_appointment_form(chat_with_id, chat_with_name)

    # Chat messages
    render_enhanced_message_history(chat_with_id)

    # Message input
    render_enhanced_message_input(chat_with_id)

def show_appointment_form(lawyer_user_id, lawyer_name):
    """Show appointment scheduling form"""
    st.markdown("### 📅 Schedule Appointment")

    with st.form(key="appointment_form"):
        col1, col2 = st.columns(2)

        with col1:
            appointment_date = st.date_input(
                "Preferred Date",
                min_value=datetime.now().date() + timedelta(days=1),
                value=datetime.now().date() + timedelta(days=1)
            )

            appointment_type = st.selectbox(
                "Meeting Type",
                ["Initial Consultation", "Follow-up Meeting", "Document Review",
                 "Court Preparation", "Legal Advice", "Contract Review"]
            )

        with col2:
            appointment_time = st.time_input("Preferred Time")

            duration = st.selectbox(
                "Expected Duration",
                ["30 minutes", "1 hour", "1.5 hours", "2 hours"]
            )

        meeting_method = st.selectbox(
            "Meeting Method",
            ["Video Call", "Phone Call", "In-Person", "Client's Choice"]
        )

        notes = st.text_area(
            "Additional Notes",
            placeholder="Please describe your legal matter briefly..."
        )

        # Form buttons
        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("📅 Request Appointment", type="primary")

        with col2:
            if st.form_submit_button("❌ Cancel"):
                st.session_state.show_appointment_form = False
                st.rerun()

        if submitted:
            try:
                # Find lawyer_id from user_id - FIXED VERSION
                from database.db_manager import execute_query

                # First check if lawyer profile exists
                lawyer_result = execute_query(
                    "SELECT id FROM lawyers WHERE user_id = %s",
                    (lawyer_user_id,), fetch='one'
                )

                if lawyer_result:
                    lawyer_id = lawyer_result[0]

                    # Create appointment request using the consultation system
                    from services.consultation_service import schedule_consultation

                    success, message = schedule_consultation(
                        st.session_state.user_id,  # client_user_id
                        lawyer_user_id,            # lawyer_user_id
                        datetime.combine(appointment_date, appointment_time),  # consultation_datetime
                        0,  # fee_amount (free for initial request)
                        f"Appointment Request - {appointment_type}\n"
                        f"Meeting Method: {meeting_method}\n"
                        f"Duration: {duration}\n"
                        f"Notes: {notes}"
                    )

                    if success:
                        st.success(f"✅ Appointment request sent to {lawyer_name}!")

                        # Send notification message
                        notification_msg = f"📅 I've sent you an appointment request for {appointment_date} at {appointment_time}. Please check your appointments section."
                        send_message(st.session_state.user_id, lawyer_user_id, notification_msg)

                        st.session_state.show_appointment_form = False
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ This user is not registered as a lawyer. They need to complete their lawyer profile first.")
                    st.info("💡 Ask them to log in and complete their lawyer profile in the system.")
            except Exception as e:
                st.error(f"Error creating appointment: {e}")
                st.info("Please try again or contact the lawyer directly.")

def render_enhanced_message_history(chat_with_id):
    """Enhanced message history with better styling"""
    try:
        messages = get_messages(st.session_state.user_id, chat_with_id)

        # Create a proper container for messages
        message_container = st.container()

        with message_container:
            if messages:
                for sender_id, receiver_id, message, sent_at, read_at in messages:
                    is_sent = sender_id == st.session_state.user_id
                    timestamp = format_timestamp(sent_at)
                    read_status = "✓✓" if read_at and is_sent else "✓" if is_sent else ""

                    if is_sent:
                        # Sent messages - align right
                        col1, col2 = st.columns([1, 3])
                        with col2:
                            st.markdown(f"""
                            <div style="background-color: #007bff; color: white; padding: 10px;
                                       border-radius: 15px; margin: 5px 0; text-align: left;">
                                {message}
                                <br><small style="opacity: 0.8;">{timestamp} {read_status}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        # Received messages - align left
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"""
                            <div style="background-color: #e9ecef; color: black; padding: 10px;
                                       border-radius: 15px; margin: 5px 0;">
                                {message}
                                <br><small style="opacity: 0.6;">{timestamp}</small>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("👋 Start the conversation! No messages yet.")
    except Exception as e:
        st.error(f"Error loading messages: {e}")

def render_enhanced_message_input(chat_with_id):
    """Enhanced message input with quick replies and file upload"""

    # Quick reply buttons
    st.markdown("**Quick Replies:**")
    col1, col2, col3, col4 = st.columns(4)

    quick_replies = [
        "👋 Hello!",
        "📅 Let's schedule a meeting",
        "📄 Could you provide more details?",
        "✅ That sounds good"
    ]

    for i, (col, reply) in enumerate(zip([col1, col2, col3, col4], quick_replies)):
        with col:
            if st.button(reply, key=f"quick_{i}"):
                try:
                    if send_message(st.session_state.user_id, chat_with_id, reply):
                        st.rerun()
                except Exception as e:
                    st.error(f"Error sending quick reply: {e}")

    st.markdown("---")

    # Check if user is blocked
    try:
        if is_user_blocked(st.session_state.user_id, chat_with_id):
            st.warning("⚠️ You cannot send messages to this user.")
            return
    except Exception as e:
        # If blocked_users table doesn't exist, continue without blocking check
        st.warning("⚠️ Message blocking feature temporarily unavailable.")

    # Message input form
    with st.form(key=f"enhanced_message_form_{chat_with_id}", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            new_message = st.text_area(
                "Type your message:",
                key=f"enhanced_msg_input_{chat_with_id}",
                height=80,
                placeholder="Type your message here... Press Ctrl+Enter to send"
            )

        with col2:
            st.write("")  # Spacing
            send_btn = st.form_submit_button("📤 Send", type="primary")

            # File upload (placeholder for future feature)
            st.caption("📎 File attachments coming soon!")

        if send_btn and new_message.strip():
            try:
                if send_message(st.session_state.user_id, chat_with_id, new_message.strip()):
                    st.success("Message sent! 📤")
                    st.rerun()
                else:
                    st.error("Failed to send message ❌")
            except Exception as e:
                st.error(f"Error sending message: {e}")

def show_user_info(user_id):
    """Show information about the user being chatted with"""
    from database.db_manager import execute_query

    try:
        user_info = execute_query(
            "SELECT username, user_type, created_at FROM users WHERE id = %s",
            (user_id,), fetch='one'
        )

        if user_info:
            username, user_type, created_at = user_info

            with st.expander("ℹ️ User Information", expanded=True):
                st.write(f"**Name:** {username}")
                st.write(f"**Type:** {user_type.title()}")
                st.write(f"**Member Since:** {format_timestamp(created_at)}")

                # If it's a lawyer, show additional info
                if user_type == 'lawyer':
                    lawyer_info = execute_query(
                        "SELECT name, specialization, experience, location FROM lawyers WHERE user_id = %s",
                        (user_id,), fetch='one'
                    )
                    if lawyer_info:
                        name, specialization, experience, location = lawyer_info
                        st.write(f"**Professional Name:** {name}")
                        st.write(f"**Specialization:** {specialization}")
                        st.write(f"**Experience:** {experience} years")
                        st.write(f"**Location:** {location}")

    except Exception as e:
        st.error(f"Error loading user info: {e}")

def format_timestamp(timestamp):
    """Format timestamp for display"""
    if not timestamp:
        return ""

    try:
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        now = datetime.now()
        diff = now - timestamp.replace(tzinfo=None)

        if diff.days > 0:
            return timestamp.strftime("%m/%d %H:%M")
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"

    except Exception:
        return str(timestamp)[:16] if timestamp else ""

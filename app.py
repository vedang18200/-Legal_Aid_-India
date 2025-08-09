import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time

# Page configuration
st.set_page_config(
    page_title="Legal Mitra - Access to Justice",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection functions
def get_pg_connection():
    """Create a new PostgreSQL connection"""
    try:
        return psycopg2.connect(
            host="db.maybtceeuypyuebrqunj.supabase.co",
            port="5432",
            dbname="postgres",
            user="postgres",
            password=st.secrets["DB_PASSWORD"]
        )
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """Execute a query with proper connection management"""
    conn = None
    cur = None
    try:
        conn = get_pg_connection()
        if conn is None:
            return None

        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        if fetch:
            result = cur.fetchall() if fetch == 'all' else cur.fetchone()
        else:
            result = None

        conn.commit()
        return result

    except psycopg2.IntegrityError as e:
        if conn:
            conn.rollback()
        raise e
    except Exception as e:
        if conn:
            conn.rollback()
        st.error(f"Database query error: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Database initialization
def init_database():
    """Initialize database tables"""
    try:
        # Users table
        execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                location VARCHAR(255),
                language VARCHAR(50),
                user_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Lawyers table
        execute_query('''
            CREATE TABLE IF NOT EXISTS lawyers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                specialization VARCHAR(255),
                experience INTEGER,
                location VARCHAR(255),
                rating DECIMAL(3,2),
                fee_range VARCHAR(100),
                verified BOOLEAN DEFAULT FALSE,
                languages VARCHAR(500),
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Cases table
        execute_query('''
            CREATE TABLE IF NOT EXISTS cases (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                lawyer_id INTEGER REFERENCES users(id),
                title VARCHAR(500),
                description TEXT,
                category VARCHAR(255),
                status VARCHAR(100) DEFAULT 'Open',
                priority VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Chat messages table
        execute_query('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                message TEXT,
                response TEXT,
                language VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Consultations table
        execute_query('''
            CREATE TABLE IF NOT EXISTS consultations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                lawyer_id INTEGER REFERENCES users(id),
                consultation_date TIMESTAMP,
                status VARCHAR(100),
                notes TEXT,
                fee_amount DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Direct messages table for chat system
        execute_query('''
            CREATE TABLE IF NOT EXISTS direct_messages (
                id SERIAL PRIMARY KEY,
                sender_id INTEGER REFERENCES users(id),
                receiver_id INTEGER REFERENCES users(id),
                message TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP NULL
            )
        ''')

    except Exception as e:
        st.error(f"Database initialization error: {e}")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #212529;
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #2a5298;
    }
    .lawyer-card {
        background: #212529;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    .case-status {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        color: white;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-active { background-color: #28a745; }
    .status-open { background-color: #28a745; }
    .status-pending { background-color: #ffc107; color: #212529; }
    .status-closed { background-color: #6c757d; }
    .status-in-progress { background-color: #17a2b8; }
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .user-message {
        background-color: #212529;
        margin-left: 2rem;
    }
    .bot-message {
        background-color: #212529;
        margin-right: 2rem;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .message-sent {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.25rem 0;
        text-align: right;
        margin-left: 20%;
    }
    .message-received {
        background-color: #f8f9fa;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.25rem 0;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
def init_session_state():
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

# Authentication functions
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user with debugging information"""
    try:
        user_check = execute_query(
            "SELECT id, username, password, user_type FROM users WHERE LOWER(username) = LOWER(%s)",
            (username,),
            fetch='one'
        )

        if not user_check:
            return None

        stored_password = user_check[2]
        hashed_input = hash_password(password)

        if stored_password == hashed_input:
            return (user_check[0], user_check[3])
        else:
            return None

    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None

def register_user(username, password, email, phone, location, language, user_type):
    """Register a new user with proper error handling"""
    try:
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = %s",
            (username,),
            fetch='one'
        )

        if existing_user:
            return False, "Username already exists. Please choose a different username."

        existing_email = execute_query(
            "SELECT id FROM users WHERE email = %s",
            (email,),
            fetch='one'
        )

        if existing_email:
            return False, "Email already registered. Please use a different email."

        hashed_password = hash_password(password)

        execute_query(
            """INSERT INTO users (username, password, email, phone, location, language, user_type)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (username, hashed_password, email, phone, location, language, user_type)
        )

        return True, "Registration successful!"

    except Exception as e:
        return False, f"Registration failed: {str(e)}"

# Dynamic navigation based on user roles
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

# Legal chatbot responses
def get_legal_response(query, language="English"):
    legal_responses = {
        "English": {
            "fir": "To file an FIR (First Information Report): 1) Visit the nearest police station, 2) Provide details of the incident, 3) Get a copy of the FIR with number, 4) Keep it safe for future reference. You have the right to file an FIR for any cognizable offense.",
            "bail": "Bail is the temporary release of an accused person awaiting trial. Types: Regular bail, Anticipatory bail, Interim bail. Contact a lawyer for proper guidance based on your specific case.",
            "divorce": "In India, divorce can be filed under: 1) Hindu Marriage Act, 2) Indian Christian Marriage Act, 3) Special Marriage Act. Grounds include cruelty, desertion, conversion, mental disorder, etc. Mutual consent divorce is faster.",
            "property": "Property disputes can be civil or criminal. Documents needed: Sale deed, mutation records, survey settlement records. Consider mediation before court proceedings.",
            "consumer": "Consumer rights include: Right to safety, information, choice, redressal. File complaints at District/State/National Consumer Forums based on compensation amount.",
            "employment": "Labor laws protect workers' rights. Issues like unfair dismissal, non-payment of wages, workplace harassment can be addressed through Labor Courts or appropriate authorities."
        }
    }

    query_lower = query.lower()
    responses = legal_responses.get(language, legal_responses["English"])

    for key, response in responses.items():
        if key in query_lower:
            return response

    return f"I understand you're asking about legal matters. For specific guidance, please consult with a verified lawyer through our platform. You can also visit our Legal Awareness section for general information about Indian laws and procedures."

# Sample data initialization
def init_sample_data():
    """Initialize sample data if tables are empty"""
    try:
        count_result = execute_query("SELECT COUNT(*) FROM lawyers", fetch='one')

        if count_result and count_result[0] == 0:
            sample_lawyers = [
                ("Advocate Priya Sharma", "priya.sharma@email.com", "+91-9876543210", "Family Law", 8, "Mumbai", 4.5, "₹500-2000", True, "English, Hindi, Marathi"),
                ("Advocate Rajesh Kumar", "rajesh.kumar@email.com", "+91-9876543211", "Criminal Law", 12, "Delhi", 4.7, "₹1000-3000", True, "English, Hindi"),
                ("Advocate Meera Nair", "meera.nair@email.com", "+91-9876543212", "Property Law", 6, "Bangalore", 4.3, "₹800-2500", True, "English, Hindi, Tamil"),
                ("Advocate Arjun Singh", "arjun.singh@email.com", "+91-9876543213", "Consumer Rights", 5, "Chennai", 4.2, "₹300-1500", True, "English, Hindi, Telugu"),
                ("Advocate Kavita Patel", "kavita.patel@email.com", "+91-9876543214", "Employment Law", 10, "Pune", 4.6, "₹600-2000", True, "English, Hindi, Gujarati")
            ]

            for lawyer in sample_lawyers:
                execute_query(
                    """INSERT INTO lawyers (name, email, phone, specialization, experience,
                       location, rating, fee_range, verified, languages)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    lawyer
                )

    except Exception as e:
        st.error(f"Sample data initialization error: {e}")

# Chat System Functions
def send_message(sender_id, receiver_id, message):
    """Send a direct message between users"""
    try:
        execute_query(
            "INSERT INTO direct_messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
            (sender_id, receiver_id, message)
        )
        return True
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return False

def get_messages(user1_id, user2_id):
    """Get all messages between two users"""
    try:
        messages = execute_query(
            """SELECT sender_id, receiver_id, message, sent_at
               FROM direct_messages
               WHERE (sender_id = %s AND receiver_id = %s)
                  OR (sender_id = %s AND receiver_id = %s)
               ORDER BY sent_at ASC""",
            (user1_id, user2_id, user2_id, user1_id),
            fetch='all'
        )
        return messages if messages else []
    except Exception as e:
        st.error(f"Error fetching messages: {e}")
        return []

def get_user_conversations():
    """Get all conversations for the current user"""
    try:
        conversations = execute_query(
            """SELECT DISTINCT
                   CASE
                       WHEN sender_id = %s THEN receiver_id
                       ELSE sender_id
                   END as other_user_id,
                   u.username as other_username,
                   u.user_type as other_user_type
               FROM direct_messages dm
               JOIN users u ON (
                   CASE
                       WHEN dm.sender_id = %s THEN dm.receiver_id = u.id
                       ELSE dm.sender_id = u.id
                   END
               )
               WHERE sender_id = %s OR receiver_id = %s""",
            (st.session_state.user_id, st.session_state.user_id,
             st.session_state.user_id, st.session_state.user_id),
            fetch='all'
        )
        return conversations if conversations else []
    except Exception as e:
        st.error(f"Error fetching conversations: {e}")
        return []

# Messages page
def show_messages_page():
    st.title("💬 Messages")

    if not st.session_state.authenticated:
        st.warning("Please login to access messages")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Conversations")
        conversations = get_user_conversations()

        if conversations:
            for other_user_id, other_username, other_user_type in conversations:
                user_display = f"{other_username} ({other_user_type})"
                if st.button(user_display, key=f"conv_{other_user_id}"):
                    st.session_state.chat_with = other_user_id
                    st.session_state.chat_with_name = other_username
                    st.rerun()
        else:
            st.info("No conversations yet. Start messaging from the lawyers or cases pages.")

    with col2:
        if st.session_state.get('chat_with'):
            show_chat_interface()
        else:
            st.info("Select a conversation to start messaging")

def show_chat_interface():
    """Show the chat interface for direct messaging"""
    chat_with_id = st.session_state.chat_with
    chat_with_name = st.session_state.get('chat_with_name', 'User')

    st.subheader(f"Chat with {chat_with_name}")

    # Get messages
    messages = get_messages(st.session_state.user_id, chat_with_id)

    # Display messages
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        if messages:
            for sender_id, receiver_id, message, sent_at in messages:
                if sender_id == st.session_state.user_id:
                    st.markdown(f'<div class="message-sent">{message}<br><small>{sent_at}</small></div>',
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="message-received">{message}<br><small>{sent_at}</small></div>',
                               unsafe_allow_html=True)
        else:
            st.info("No messages yet. Start the conversation!")

        st.markdown('</div>', unsafe_allow_html=True)

    # Message input
    with st.form(f"message_form_{chat_with_id}"):
        new_message = st.text_input("Type your message:", key=f"msg_input_{chat_with_id}")
        if st.form_submit_button("Send Message"):
            if new_message.strip():
                if send_message(st.session_state.user_id, chat_with_id, new_message):
                    st.success("Message sent!")
                    st.rerun()
                else:
                    st.error("Failed to send message")

# Available Cases for Lawyers
def show_available_cases():
    st.title("💼 Available Cases")

    if not st.session_state.authenticated or st.session_state.user_type != "Lawyer":
        st.warning("This page is only for lawyers")
        return

    try:
        # Get unassigned cases
        cases = execute_query(
            """SELECT c.id, c.title, c.description, c.category, c.priority,
                      c.created_at, u.username, u.location
               FROM cases c
               JOIN users u ON c.user_id = u.id
               WHERE c.lawyer_id IS NULL AND c.status = 'Open'
               ORDER BY c.created_at DESC""",
            fetch='all'
        )

        if not cases:
            st.info("No available cases at the moment.")
            return

        st.write(f"Found {len(cases)} available cases")

        for case in cases:
            case_id, title, description, category, priority, created_at, client_name, location = case

            # Priority colors
            priority_colors = {
                'Low': '#28a745',
                'Medium': '#ffc107',
                'High': '#fd7e14',
                'Urgent': '#dc3545'
            }
            priority_color = priority_colors.get(priority, '#6c757d')

            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #f8f9fa;">
                <h4>{title} <span style="background-color: {priority_color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{priority}</span></h4>
                <p><strong>Client:</strong> {client_name} | <strong>Category:</strong> {category} | <strong>Location:</strong> {location}</p>
                <p><strong>Description:</strong> {description}</p>
                <p><small><strong>Created:</strong> {created_at}</small></p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Take Case", key=f"take_{case_id}"):
                    # Assign case to current lawyer
                    try:
                        execute_query(
                            "UPDATE cases SET lawyer_id = %s, status = 'In Progress', updated_at = %s WHERE id = %s",
                            (st.session_state.user_id, datetime.now(), case_id)
                        )
                        st.success(f"Case #{case_id} assigned to you!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error taking case: {e}")

            with col2:
                if st.button(f"View Details", key=f"details_{case_id}"):
                    st.info(f"Detailed view for case #{case_id}")

            with col3:
                # Get client's user_id for messaging
                client_user = execute_query(
                    "SELECT user_id FROM cases WHERE id = %s",
                    (case_id,),
                    fetch='one'
                )
                if client_user and st.button(f"Contact Client", key=f"contact_{case_id}"):
                    st.session_state.chat_with = client_user[0]
                    st.session_state.chat_with_name = client_name
                    st.session_state.current_page = "Messages"
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading available cases: {e}")

# Home page
def show_home_page():
    st.markdown('<div class="main-header"><h1>⚖️ Legal Aid India</h1><p>Bridging the Justice Gap - Free & Affordable Legal Services</p></div>', unsafe_allow_html=True)

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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registered Lawyers", "150+")
    with col2:
        st.metric("Cases Resolved", "1,200+")
    with col3:
        st.metric("Users Helped", "5,000+")
    with col4:
        st.metric("Languages Supported", "10+")

# Chatbot page
def show_chatbot_page():
    st.title("🤖 Legal Assistant Chatbot")

    col1, col2 = st.columns([2, 1])

    with col2:
        language = st.selectbox("Select Language", ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Malayalam"])

        st.markdown("### Quick Questions:")
        quick_questions = [
            "How to file an FIR?",
            "What is bail process?",
            "Divorce procedure in India",
            "Property dispute resolution",
            "Consumer rights protection",
            "Employment law basics"
        ]

        for question in quick_questions:
            if st.button(question, key=f"quick_{question}"):
                st.session_state.chat_history.append(("user", question))
                response = get_legal_response(question, language)
                st.session_state.chat_history.append(("bot", response))

    with col1:
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
            st.session_state.chat_history.append(("user", user_input))
            response = get_legal_response(user_input, language)
            st.session_state.chat_history.append(("bot", response))

            # Save to database if user is logged in
            if st.session_state.authenticated:
                try:
                    execute_query(
                        "INSERT INTO chat_messages (user_id, message, response, language) VALUES (%s, %s, %s, %s)",
                        (st.session_state.user_id, user_input, response, language)
                    )
                except Exception as e:
                    st.error(f"Error saving chat: {e}")

            st.rerun()

# Lawyer marketplace page
def show_lawyer_marketplace():
    st.title("👨‍⚖️ Lawyer Marketplace")

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        specialization_filter = st.selectbox("Specialization",
            ["All", "Family Law", "Criminal Law", "Property Law", "Consumer Rights", "Employment Law"])
    with col2:
        location_filter = st.selectbox("Location",
            ["All", "Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"])
    with col3:
        fee_filter = st.selectbox("Fee Range",
            ["All", "₹0-500", "₹500-1500", "₹1500-3000", "₹3000+"])

    try:
        # Get lawyers from database
        conn = get_pg_connection()
        if conn is None:
            st.error("Unable to connect to database")
            return

        query = "SELECT * FROM lawyers WHERE verified = %s"
        params = [True]

        if specialization_filter != "All":
            query += " AND specialization = %s"
            params.append(specialization_filter)
        if location_filter != "All":
            query += " AND location = %s"
            params.append(location_filter)

        lawyers_df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        if lawyers_df.empty:
            st.info("No lawyers found matching your criteria.")
            return

        # Display lawyers
        for idx, lawyer in lawyers_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="lawyer-card">
                    <h4>{lawyer['name']} ⭐ {lawyer['rating']}/5.0</h4>
                    <p><strong>Specialization:</strong> {lawyer['specialization']} |
                       <strong>Experience:</strong> {lawyer['experience']} years |
                       <strong>Location:</strong> {lawyer['location']}</p>
                    <p><strong>Fee Range:</strong> {lawyer['fee_range']} |
                       <strong>Languages:</strong> {lawyer['languages']}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Book Consultation", key=f"book_{lawyer['id']}"):
                        if st.session_state.authenticated:
                            st.success(f"Consultation request sent to {lawyer['name']}")
                        else:
                            st.warning("Please login to book consultation")

                with col2:
                    if st.button(f"View Profile", key=f"profile_{lawyer['id']}"):
                        st.info(f"Viewing profile of {lawyer['name']}")

                with col3:
                    if st.button(f"Chat", key=f"chat_{lawyer['id']}"):
                        if st.session_state.authenticated:
                            # Find lawyer's user_id
                            lawyer_user = execute_query(
                                "SELECT user_id FROM lawyers WHERE id = %s",
                                (lawyer['id'],),
                                fetch='one'
                            )
                            if lawyer_user:
                                st.session_state.chat_with = lawyer_user[0]
                                st.session_state.chat_with_name = lawyer['name']
                                st.session_state.current_page = "Messages"
                                st.rerun()
                            else:
                                st.error("Unable to start chat with this lawyer")
                        else:
                            st.warning("Please login to start chat")

    except Exception as e:
        st.error(f"Error loading lawyers: {e}")

# Case tracking page
def show_case_tracking():
    st.title("📋 Case Tracking & Management")

    if not st.session_state.authenticated:
        st.warning("Please login to access case tracking")
        return

    try:
        # Add new case
        with st.expander("➕ Add New Case"):
            with st.form("new_case_form"):
                case_title = st.text_input("Case Title")
                case_description = st.text_area("Case Description")
                case_category = st.selectbox("Category",
                    ["Family Law", "Criminal Law", "Property Law", "Consumer Rights", "Employment Law"])
                case_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])

                if st.form_submit_button("Create Case"):
                    try:
                        execute_query(
                            """INSERT INTO cases (user_id, title, description, category, status, priority, created_at)
                               VALUES (%s, %s, %s, %s, 'Open', %s, %s)""",
                            (st.session_state.user_id, case_title, case_description, case_category, case_priority, datetime.now())
                        )
                        st.success("Case created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating case: {e}")

        # Get user cases
        cases = execute_query("""
            SELECT c.*, u.username as lawyer_name
            FROM cases c
            LEFT JOIN users u ON c.lawyer_id = u.id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
        """, (st.session_state.user_id,), fetch='all')

        # Display existing cases
        if not cases:
            st.info("No cases found. Create your first case above.")
        else:
            for case in cases:
                case_id, user_id, lawyer_id, title, description, category, status, priority, created_at, updated_at, lawyer_name = case
                status_class = f"status-{status.lower().replace(' ', '-')}" if status else "status-pending"

                st.markdown(f"""
                <div class="feature-card">
                    <h4>{title} <span class="case-status {status_class}">{status or 'Pending'}</span></h4>
                    <p><strong>Category:</strong> {category} | <strong>Priority:</strong> {priority}</p>
                    <p><strong>Description:</strong> {description}</p>
                    <p><strong>Lawyer:</strong> {lawyer_name or 'Not assigned'}</p>
                    <p><strong>Created:</strong> {created_at}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Update Status", key=f"update_{case_id}"):
                        st.info("Status update feature - to be implemented")
                with col2:
                    if st.button(f"Upload Documents", key=f"docs_{case_id}"):
                        st.info("Document upload feature - to be implemented")
                with col3:
                    if lawyer_id and st.button(f"Contact Lawyer", key=f"contact_lawyer_{case_id}"):
                        st.session_state.chat_with = lawyer_id
                        st.session_state.chat_with_name = lawyer_name
                        st.session_state.current_page = "Messages"
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading cases: {e}")

# Legal awareness page
def show_legal_awareness():
    st.title("📖 Legal Awareness Portal")

    # Fundamental Rights
    with st.expander("🏛️ Fundamental Rights in India"):
        st.markdown("""
        ### Your Constitutional Rights:
        1. **Right to Equality** (Articles 14-18)
        2. **Right to Freedom** (Articles 19-22)
        3. **Right against Exploitation** (Articles 23-24)
        4. **Right to Freedom of Religion** (Articles 25-28)
        5. **Cultural and Educational Rights** (Articles 29-30)
        6. **Right to Constitutional Remedies** (Article 32)
        """)

    # Government Schemes
    with st.expander("🏛️ Government Legal Aid Schemes"):
        st.markdown("""
        ### Available Legal Aid Schemes:
        - **National Legal Services Authority (NALSA)**
        - **State Legal Services Authorities**
        - **District Legal Services Authorities**
        - **Free Legal Aid for Women, Children, SC/ST**
        - **Lok Adalats for Quick Justice**
        """)

    # Common Legal Procedures
    with st.expander("📋 Common Legal Procedures"):
        tabs = st.tabs(["Criminal Law", "Civil Law", "Family Law", "Consumer Rights"])

        with tabs[0]:
            st.markdown("""
            ### Criminal Law Procedures:
            - **Filing FIR**: Process and requirements
            - **Bail Applications**: Types and procedure
            - **Court Proceedings**: What to expect
            - **Victim Rights**: Compensation and support
            """)

        with tabs[1]:
            st.markdown("""
            ### Civil Law Procedures:
            - **Property Disputes**: Documentation needed
            - **Contract Disputes**: Legal remedies
            - **Rent Disputes**: Tenant and landlord rights
            - **Recovery Suits**: Money recovery process
            """)

        with tabs[2]:
            st.markdown("""
            ### Family Law Procedures:
            - **Marriage Registration**: Process and benefits
            - **Divorce Procedures**: Mutual consent vs contested
            - **Child Custody**: Legal guidelines
            - **Maintenance Laws**: Rights and obligations
            """)

        with tabs[3]:
            st.markdown("""
            ### Consumer Rights:
            - **Consumer Forums**: District, State, National
            - **E-commerce Disputes**: Online purchase issues
            - **Service Complaints**: Banking, telecom, etc.
            - **Product Liability**: Defective products
            """)

# Login page
def show_login_page():
    st.title("🔐 Login / Register")

    if st.button("← Back to Home"):
        st.session_state.current_page = "Home"
        st.rerun()

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
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

            elif demo_button:
                st.session_state.authenticated = True
                st.session_state.user_id = 999
                st.session_state.user_type = "Citizen"
                st.session_state.username = "Demo User"
                st.success("✅ Demo login successful! Welcome to the demo!")
                st.session_state.current_page = "Home"
                st.rerun()

            elif test_button:
                test_users = execute_query("SELECT username FROM users LIMIT 3", fetch='all')
                if test_users:
                    st.info(f"Available test users: {[user[0] for user in test_users]}")
                else:
                    st.warning("No users found in database")

        st.markdown("---")
        st.info("💡 **Demo Access**: Click 'Demo Login' to explore the platform without creating an account.")

    with tab2:
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
                location = st.selectbox("📍 Location", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Other"])
                language = st.selectbox("🗣️ Preferred Language", ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Malayalam", "Kannada", "Gujarati", "Marathi"])
                user_type = st.selectbox("👥 Account Type", ["Citizen", "Lawyer", "Legal Aid Worker"])

            register_button = st.form_submit_button("🎉 Create Account", use_container_width=True, type="primary")

            if register_button:
                if not all([new_username, new_password, confirm_password, email, phone]):
                    st.error("❌ Please fill in all required fields.")
                elif new_password != confirm_password:
                    st.error("❌ Passwords don't match. Please try again.")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                elif "@" not in email or "." not in email:
                    st.error("❌ Please enter a valid email address.")
                elif len(new_username) < 3:
                    st.error("❌ Username must be at least 3 characters long.")
                else:
                    success, message = register_user(new_username, new_password, email, phone, location, language, user_type)

                    if success:
                        st.success("🎉 " + message)
                        st.info(f"✅ You can now login with username: '{new_username}'")
                        st.balloons()

                        if st.checkbox("Show debug info"):
                            st.code(f"Username: {new_username}")
                            st.code(f"Password hash: {hash_password(new_password)}")
                    else:
                        st.error("❌ " + message)

        st.markdown("---")
        st.info("📋 **Account Types**:\n- **Citizen**: Access legal aid services\n- **Lawyer**: Provide legal services\n- **Legal Aid Worker**: Manage and coordinate services")

# Lawyer-specific pages
def show_lawyer_dashboard():
    st.title("💼 Lawyer Dashboard")

    # Welcome message
    st.markdown(f"### Welcome back, Advocate {st.session_state.get('username', 'User')}!")

    # Quick stats for lawyers
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Count active cases assigned to this lawyer
        active_cases = execute_query(
            "SELECT COUNT(*) FROM cases WHERE lawyer_id = %s AND status IN ('Open', 'In Progress')",
            (st.session_state.user_id,), fetch='one'
        )
        st.metric("Active Cases", active_cases[0] if active_cases else 0)

    with col2:
        # Count pending consultations
        pending_consultations = execute_query(
            "SELECT COUNT(*) FROM consultations WHERE lawyer_id = %s AND status = 'Pending'",
            (st.session_state.user_id,), fetch='one'
        )
        st.metric("Pending Consultations", pending_consultations[0] if pending_consultations else 0)

    with col3:
        # Total clients
        total_clients = execute_query(
            "SELECT COUNT(DISTINCT user_id) FROM cases WHERE lawyer_id = %s",
            (st.session_state.user_id,), fetch='one'
        )
        st.metric("Total Clients", total_clients[0] if total_clients else 0)

    with col4:
        # Available cases to take
        available_cases = execute_query(
            "SELECT COUNT(*) FROM cases WHERE lawyer_id IS NULL AND status = 'Open'",
            fetch='one'
        )
        st.metric("Available Cases", available_cases[0] if available_cases else 0)

    st.markdown("---")

    # Recent activities
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔄 Recent Case Updates")
        recent_cases = execute_query(
            """SELECT c.title, c.status, c.updated_at, u.username as client_name
               FROM cases c
               JOIN users u ON c.user_id = u.id
               WHERE c.lawyer_id = %s
               ORDER BY c.updated_at DESC LIMIT 5""",
            (st.session_state.user_id,), fetch='all'
        )

        if recent_cases:
            for case in recent_cases:
                st.markdown(f"""
                <div style="padding: 10px; border: 1px solid #ddd; margin: 5px 0; border-radius: 5px;">
                    <strong>{case[0]}</strong><br>
                    Client: {case[3]} | Status: {case[1]}<br>
                    <small>Updated: {case[2]}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent case updates")

    with col2:
        st.subheader("📅 Upcoming Appointments")
        upcoming_appointments = execute_query(
            """SELECT c.consultation_date, u.username as client_name, c.notes
               FROM consultations c
               JOIN users u ON c.user_id = u.id
               WHERE c.lawyer_id = %s AND c.consultation_date > NOW()
               ORDER BY c.consultation_date ASC LIMIT 5""",
            (st.session_state.user_id,), fetch='all'
        )

        if upcoming_appointments:
            for appointment in upcoming_appointments:
                st.markdown(f"""
                <div style="padding: 10px; border: 1px solid #ddd; margin: 5px 0; border-radius: 5px;">
                    <strong>{appointment[1]}</strong><br>
                    Date: {appointment[0]}<br>
                    <small>{appointment[2] or 'No notes'}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No upcoming appointments")

def show_lawyer_cases():
    st.title("📋 My Cases Management")

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Closed", "Pending"])
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All", "Family Law", "Criminal Law", "Property Law", "Consumer Rights", "Employment Law"])
    with col3:
        priority_filter = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High", "Urgent"])

    # Build query based on filters
    query = """
        SELECT c.id, c.title, c.description, c.category, c.status, c.priority,
            c.created_at, c.updated_at, u.username as client_name, u.phone, u.email, c.user_id
        FROM cases c
        JOIN users u ON c.user_id = u.id
        WHERE c.lawyer_id = %s
    """
    params = [st.session_state.user_id]

    if status_filter != "All":
        query += " AND c.status = %s"
        params.append(status_filter)
    if category_filter != "All":
        query += " AND c.category = %s"
        params.append(category_filter)
    if priority_filter != "All":
        query += " AND c.priority = %s"
        params.append(priority_filter)

    query += " ORDER BY c.updated_at DESC"

    try:
        cases = execute_query(query, params, fetch='all')

        if not cases:
            st.info("No cases found matching your criteria.")
            return

        # Display cases
        for case in cases:
            case_id, title, description, category, status, priority, created_at, updated_at, client_name, phone, email, client_user_id = case

            # Determine status color
            status_colors = {
                'Open': '#28a745',
                'In Progress': '#17a2b8',
                'Closed': '#6c757d',
                'Pending': '#ffc107'
            }
            status_color = status_colors.get(status, '#6c757d')

            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #212529;">
                <h4>{title} <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{status}</span></h4>
                <p><strong>Client:</strong> {client_name} | <strong>Category:</strong> {category} | <strong>Priority:</strong> {priority}</p>
                <p><strong>Description:</strong> {description}</p>
                <p><strong>Contact:</strong> {phone} | {email}</p>
                <p><small><strong>Created:</strong> {created_at} | <strong>Updated:</strong> {updated_at}</small></p>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # Status update dropdown
                new_status = st.selectbox("Update Status",
                    ["Open", "In Progress", "Closed", "Pending", "On Hold"],
                    index=["Open", "In Progress", "Closed", "Pending", "On Hold"].index(status) if status in ["Open", "In Progress", "Closed", "Pending", "On Hold"] else 0,
                    key=f"status_select_{case_id}"
                )
                if st.button("Update", key=f"status_update_{case_id}"):
                    try:
                        execute_query(
                            "UPDATE cases SET status = %s, updated_at = %s WHERE id = %s",
                            (new_status, datetime.now(), case_id)
                        )
                        st.success(f"Case status updated to: {new_status}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating status: {e}")

            with col2:
                if st.button(f"Add Notes", key=f"notes_{case_id}"):
                    st.info("Notes feature - to be implemented")

            with col3:
                if st.button(f"Schedule Meeting", key=f"meeting_{case_id}"):
                    st.info("Meeting scheduling - to be implemented")

            with col4:
                if st.button(f"Contact Client", key=f"contact_{case_id}"):
                    st.session_state.chat_with = client_user_id
                    st.session_state.chat_with_name = client_name
                    st.session_state.current_page = "Messages"
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading cases: {e}")

def show_lawyer_clients():
    st.title("👥 My Clients")

    try:
        clients = execute_query(
            """SELECT DISTINCT u.id, u.username, u.email, u.phone, u.location,
                      COUNT(c.id) as total_cases,
                      COUNT(CASE WHEN c.status IN ('Open', 'In Progress') THEN 1 END) as active_cases
               FROM users u
               JOIN cases c ON u.id = c.user_id
               WHERE c.lawyer_id = %s
               GROUP BY u.id, u.username, u.email, u.phone, u.location
               ORDER BY u.username""",
            (st.session_state.user_id,), fetch='all'
        )

        if not clients:
            st.info("You don't have any clients yet.")
            return

        for client in clients:
            user_id, username, email, phone, location, total_cases, active_cases = client

            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px;">
                <h4>👤 {username}</h4>
                <p><strong>📧 Email:</strong> {email} | <strong>📱 Phone:</strong> {phone}</p>
                <p><strong>📍 Location:</strong> {location}</p>
                <p><strong>📊 Cases:</strong> {total_cases} total, {active_cases} active</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"View Cases", key=f"view_cases_{user_id}"):
                    st.info(f"Showing cases for {username}")
            with col2:
                if st.button(f"Schedule Consultation", key=f"schedule_{user_id}"):
                    st.info(f"Scheduling consultation with {username}")
            with col3:
                if st.button(f"Send Message", key=f"message_{user_id}"):
                    st.session_state.chat_with = user_id
                    st.session_state.chat_with_name = username
                    st.session_state.current_page = "Messages"
                    st.rerun()

    except Exception as e:
        st.error(f"Error loading clients: {e}")

def show_lawyer_appointments():
    st.title("📅 Appointments & Consultations")

    tab1, tab2, tab3 = st.tabs(["Upcoming", "Past", "Schedule New"])

    with tab1:
        st.subheader("📅 Upcoming Appointments")
        upcoming = execute_query(
            """SELECT c.id, c.consultation_date, c.status, c.notes, c.fee_amount,
                      u.username, u.phone, u.email
               FROM consultations c
               JOIN users u ON c.user_id = u.id
               WHERE c.lawyer_id = %s AND c.consultation_date > NOW()
               ORDER BY c.consultation_date ASC""",
            (st.session_state.user_id,), fetch='all'
        )

        if upcoming:
            for appointment in upcoming:
                consultation_id, date, status, notes, fee, client_name, phone, email = appointment
                st.markdown(f"""
                <div style="border: 1px solid #007bff; padding: 15px; margin: 10px 0; border-radius: 10px;">
                    <h4>📅 {date}</h4>
                    <p><strong>Client:</strong> {client_name} | <strong>Status:</strong> {status}</p>
                    <p><strong>Contact:</strong> {phone} | {email}</p>
                    <p><strong>Fee:</strong> ₹{fee or 'TBD'} | <strong>Notes:</strong> {notes or 'None'}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Mark Complete", key=f"complete_{consultation_id}"):
                        execute_query(
                            "UPDATE consultations SET status = 'Completed' WHERE id = %s",
                            (consultation_id,)
                        )
                        st.success("Appointment marked as completed")
                        st.rerun()
                with col2:
                    if st.button(f"Reschedule", key=f"reschedule_{consultation_id}"):
                        st.info("Reschedule feature - to be implemented")
                with col3:
                    if st.button(f"Cancel", key=f"cancel_{consultation_id}"):
                        execute_query(
                            "UPDATE consultations SET status = 'Cancelled' WHERE id = %s",
                            (consultation_id,)
                        )
                        st.warning("Appointment cancelled")
                        st.rerun()
        else:
            st.info("No upcoming appointments")

    with tab2:
        st.subheader("📋 Past Appointments")
        past = execute_query(
            """SELECT c.consultation_date, c.status, u.username, c.fee_amount
               FROM consultations c
               JOIN users u ON c.user_id = u.id
               WHERE c.lawyer_id = %s AND c.consultation_date < NOW()
               ORDER BY c.consultation_date DESC LIMIT 10""",
            (st.session_state.user_id,), fetch='all'
        )

        if past:
            for appointment in past:
                date, status, client_name, fee = appointment
                st.markdown(f"**{date}** - {client_name} | {status} | ₹{fee or 'Free'}")
        else:
            st.info("No past appointments")

    with tab3:
        st.subheader("➕ Schedule New Consultation")
        with st.form("schedule_consultation"):
            # Get list of clients
            clients = execute_query(
                """SELECT DISTINCT u.id, u.username
                   FROM users u
                   JOIN cases c ON u.id = c.user_id
                   WHERE c.lawyer_id = %s""",
                (st.session_state.user_id,), fetch='all'
            )

            if clients:
                client_options = {f"{client[1]} (ID: {client[0]})": client[0] for client in clients}
                selected_client = st.selectbox("Select Client", list(client_options.keys()))
                consultation_date = st.datetime_input("Consultation Date & Time", value=datetime.now() + timedelta(days=1))
                fee_amount = st.number_input("Fee Amount (₹)", min_value=0, value=500)
                notes = st.text_area("Notes")

                if st.form_submit_button("Schedule Consultation"):
                    client_id = client_options[selected_client]
                    try:
                        execute_query(
                            """INSERT INTO consultations (user_id, lawyer_id, consultation_date, status, notes, fee_amount)
                               VALUES (%s, %s, %s, 'Scheduled', %s, %s)""",
                            (client_id, st.session_state.user_id, consultation_date, notes, fee_amount)
                        )
                        st.success("Consultation scheduled successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error scheduling consultation: {e}")
            else:
                st.info("No clients found. Clients will appear here once they have cases assigned to you.")

# Placeholder functions for additional lawyer features
def show_lawyer_earnings():
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

def show_lawyer_resources():
    st.title("⚖️ Legal Resources")
    st.info("📚 Legal resources and reference materials coming soon!")

    # Placeholder content
    with st.expander("📖 Case Law Database"):
        st.markdown("Access to latest case laws and judgments")

    with st.expander("📋 Legal Forms & Templates"):
        st.markdown("Downloadable legal forms and document templates")

    with st.expander("📰 Legal News & Updates"):
        st.markdown("Latest legal news and regulatory updates")

def show_lawyer_profile():
    st.title("👤 Lawyer Profile Management")

    try:
        # Get current lawyer profile
        profile = execute_query(
            """SELECT l.name, l.email, l.phone, l.specialization, l.experience,
                      l.location, l.languages, u.username
               FROM lawyers l
               JOIN users u ON l.user_id = u.id
               WHERE l.user_id = %s""",
            (st.session_state.user_id,), fetch='one'
        )

        if profile:
            name, email, phone, specialization, experience, location, languages, username = profile
        else:
            name = email = phone = specialization = location = languages = ""
            experience = 0
            username = st.session_state.get('username', '')

        # Profile form
        with st.form("lawyer_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name", value=name)
                phone_input = st.text_input("Phone", value=phone or "")
                specialization_input = st.text_input("Specialization", value=specialization or "")
                languages_input = st.text_input("Languages", value=languages or "")

            with col2:
                experience_input = st.number_input("Years of Experience", min_value=0, max_value=50, value=experience or 0)
                location_input = st.selectbox("Location",
                    ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Other"],
                    index=0 if not location else (["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Other"].index(location) if location in ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Other"] else 0)
                )
                email_input = st.text_input("Email", value=email or "")
                registration = st.text_input("Bar Council Registration", placeholder="Registration Number")

            bio = st.text_area("Bio/Description", placeholder="Brief description of your practice and expertise")

            if st.form_submit_button("Update Profile"):
                try:
                    # Check if lawyer profile exists
                    existing_profile = execute_query(
                        "SELECT id FROM lawyers WHERE user_id = %s",
                        (st.session_state.user_id,), fetch='one'
                    )

                    if existing_profile:
                        # Update existing profile
                        execute_query(
                            """UPDATE lawyers SET name = %s, email = %s, phone = %s,
                               specialization = %s, experience = %s, location = %s, languages = %s
                               WHERE user_id = %s""",
                            (full_name, email_input, phone_input, specialization_input,
                             experience_input, location_input, languages_input, st.session_state.user_id)
                        )
                    else:
                        # Create new profile
                        execute_query(
                            """INSERT INTO lawyers (user_id, name, email, phone, specialization,
                               experience, location, languages, verified)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (st.session_state.user_id, full_name, email_input, phone_input,
                             specialization_input, experience_input, location_input, languages_input, False)
                        )

                    st.success("Profile updated successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error updating profile: {e}")

    except Exception as e:
        st.error(f"Error loading profile: {e}")

# Placeholder functions for additional citizen features
def show_consultations_page():
    st.title("📅 My Consultations")

    if not st.session_state.authenticated:
        st.warning("Please login to view consultations")
        return

    try:
        # Get user consultations
        consultations = execute_query(
            """SELECT c.id, c.consultation_date, c.status, c.notes, c.fee_amount,
                      l.name as lawyer_name, l.phone as lawyer_phone
               FROM consultations c
               JOIN lawyers l ON c.lawyer_id = l.user_id
               WHERE c.user_id = %s
               ORDER BY c.consultation_date DESC""",
            (st.session_state.user_id,), fetch='all'
        )

        if consultations:
            st.subheader("Your Consultations")
            for consultation in consultations:
                consultation_id, date, status, notes, fee, lawyer_name, lawyer_phone = consultation

                # Determine status color
                status_colors = {
                    'Scheduled': '#17a2b8',
                    'Completed': '#28a745',
                    'Cancelled': '#dc3545',
                    'Pending': '#ffc107'
                }
                status_color = status_colors.get(status, '#6c757d')

                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #212529;">
                    <h4>Consultation with {lawyer_name} <span style="background-color: {status_color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{status}</span></h4>
                    <p><strong>Date:</strong> {date} | <strong>Fee:</strong> ₹{fee or 'TBD'}</p>
                    <p><strong>Notes:</strong> {notes or 'No notes'}</p>
                    <p><strong>Lawyer Contact:</strong> {lawyer_phone}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No consultations booked yet.")

    except Exception as e:
        st.error(f"Error loading consultations: {e}")

def show_profile_page():
    st.title("👤 My Profile")

    if not st.session_state.authenticated:
        st.warning("Please login to view profile")
        return

    try:
        # Get current user profile
        user_profile = execute_query(
            "SELECT username, email, phone, location, language FROM users WHERE id = %s",
            (st.session_state.user_id,), fetch='one'
        )

        if user_profile:
            username, email, phone, location, language = user_profile
        else:
            username = email = phone = location = language = ""

        # Profile form
        with st.form("user_profile"):
            col1, col2 = st.columns(2)

            with col1:
                new_username = st.text_input("Username", value=username, disabled=True)
                new_email = st.text_input("Email", value=email or "")
                new_phone = st.text_input("Phone", value=phone or "")

            with col2:
                new_location = st.selectbox("Location",
                    ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Other"],
                    index=0 if not location else (["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Other"].index(location) if location in ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata", "Other"] else 0)
                )
                new_language = st.selectbox("Preferred Language",
                    ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Malayalam", "Kannada", "Gujarati", "Marathi"],
                    index=0 if not language else (["English", "Hindi", "Tamil", "Telugu", "Bengali", "Malayalam", "Kannada", "Gujarati", "Marathi"].index(language) if language in ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Malayalam", "Kannada", "Gujarati", "Marathi"] else 0)
                )

            address = st.text_area("Address", placeholder="Enter your full address")

            if st.form_submit_button("Update Profile"):
                try:
                    execute_query(
                        "UPDATE users SET email = %s, phone = %s, location = %s, language = %s WHERE id = %s",
                        (new_email, new_phone, new_location, new_language, st.session_state.user_id)
                    )
                    st.success("Profile updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating profile: {e}")

    except Exception as e:
        st.error(f"Error loading profile: {e}")

# Main application logic
def main():
    init_database()
    init_session_state()
    init_sample_data()

    # Sidebar navigation
    st.sidebar.title("⚖️ Legal Aid India")

    if st.session_state.authenticated:
        user_type = st.session_state.get('user_type', 'Citizen')
        st.sidebar.success(f"✅ Welcome!\n**User:** {st.session_state.get('username', 'User')}\n**Type:** {user_type}")

        if st.sidebar.button("🚪 Logout", use_container_width=True, type="primary"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_type = None
            st.session_state.username = None
            st.session_state.chat_history = []
            st.session_state.chat_with = None
            st.session_state.chat_open = False
            st.session_state.current_page = "Home"
            st.success("👋 Logged out successfully!")
            st.rerun()
    else:
        st.sidebar.info("👤 **Not logged in**\nSome features require authentication")

        # Quick login widget in sidebar
        with st.sidebar.expander("🔐 Quick Login"):
            quick_username = st.text_input("Username", key="sidebar_username", placeholder="Your username")
            quick_password = st.text_input("Password", type="password", key="sidebar_password", placeholder="Your password")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", key="sidebar_login", use_container_width=True):
                    if quick_username and quick_password:
                        result = authenticate_user(quick_username, quick_password)
                        if result:
                            st.session_state.authenticated = True
                            st.session_state.user_id = result[0]
                            st.session_state.user_type = result[1]
                            st.session_state.username = quick_username
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                    else:
                        st.warning("⚠️ Enter credentials")

            with col2:
                if st.button("Demo", key="sidebar_demo", use_container_width=True):
                    st.session_state.authenticated = True
                    st.session_state.user_id = 999
                    st.session_state.user_type = "Citizen"
                    st.session_state.username = "Demo User"
                    st.success("✅ Demo mode!")
                    st.rerun()

    st.sidebar.markdown("---")

    # Dynamic navigation menu
    pages = get_navigation_menu()

    # Use radio buttons for navigation
    current_index = 0
    if st.session_state.current_page in pages.values():
        current_index = list(pages.values()).index(st.session_state.current_page)

    selected_page = st.sidebar.radio(
        "🧭 Navigate to:",
        list(pages.keys()),
        index=current_index,
        key="main_navigation"
    )

    # Update current page when selection changes
    new_page = pages[selected_page]
    if new_page != st.session_state.current_page:
        st.session_state.current_page = new_page
        st.rerun()

    # Add role-specific help information
    st.sidebar.markdown("---")
    user_type = st.session_state.get('user_type', 'Guest')

    if user_type == "Citizen":
        st.sidebar.markdown("### 🆘 Quick Help")
        st.sidebar.markdown("""
        - **Emergency Legal Helpline**: 1800-345-4357
        - **NALSA Helpline**: 15100
        - **Women Helpline**: 1091
        - **Cyber Crime**: 1930
        """)
    elif user_type == "Lawyer":
        st.sidebar.markdown("### 💼 Lawyer Resources")
        st.sidebar.markdown("""
        - **Bar Council**: 1800-XXX-XXXX
        - **Legal Updates**: Check notifications
        - **Client Support**: 24/7 available
        - **Technical Help**: support@legal.com
        """)
    else:
        st.sidebar.markdown("### 🆘 General Help")
        st.sidebar.markdown("""
        - **Emergency Legal Helpline**: 1800-345-4357
        - **Support**: support@legal.com
        """)

    # Route to appropriate page based on user type and selection
    if st.session_state.current_page == "Home":
        show_home_page()
    elif st.session_state.current_page == "Chatbot":
        show_chatbot_page()
    elif st.session_state.current_page == "Lawyers":
        show_lawyer_marketplace()
    elif st.session_state.current_page == "Cases":
        show_case_tracking()
    elif st.session_state.current_page == "Consultations":
        show_consultations_page()
    elif st.session_state.current_page == "Awareness":
        show_legal_awareness()
    elif st.session_state.current_page == "Messages":
        show_messages_page()
    elif st.session_state.current_page == "Profile":
        show_profile_page()
    elif st.session_state.current_page == "Login":
        show_login_page()
    # Lawyer-specific pages
    elif st.session_state.current_page == "LawyerDashboard":
        show_lawyer_dashboard()
    elif st.session_state.current_page == "AvailableCases":
        show_available_cases()
    elif st.session_state.current_page == "LawyerCases":
        show_lawyer_cases()
    elif st.session_state.current_page == "LawyerClients":
        show_lawyer_clients()
    elif st.session_state.current_page == "LawyerAppointments":
        show_lawyer_appointments()
    elif st.session_state.current_page == "LawyerEarnings":
        show_lawyer_earnings()
    elif st.session_state.current_page == "LawyerResources":
        show_lawyer_resources()
    elif st.session_state.current_page == "LawyerProfile":
        show_lawyer_profile()
    # Admin pages (placeholder)
    elif st.session_state.current_page.startswith("Admin"):
        st.title("🚧 Admin Panel")
        st.info("Admin features coming soon...")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Legal Aid India Platform | Empowering Justice for All</p>
        <p>For emergency legal assistance, contact: <strong>Emergency Legal Helpline: 1800-xxx-xxxx</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

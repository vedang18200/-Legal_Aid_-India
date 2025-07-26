import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import hashlib
import json
import re
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Legal Aid India - Access to Justice",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .status-pending { background-color: #ffc107; color: #212529; }
    .status-closed { background-color: #6c757d; }
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
</style>

""", unsafe_allow_html=True)

# Database setup
def init_database():
    conn = sqlite3.connect('legal_aid.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                  password TEXT, email TEXT, phone TEXT, 
                  location TEXT, language TEXT, user_type TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Lawyers table
    c.execute('''CREATE TABLE IF NOT EXISTS lawyers
                 (id INTEGER PRIMARY KEY, name TEXT, email TEXT,
                  phone TEXT, specialization TEXT, experience INTEGER,
                  location TEXT, rating REAL, fee_range TEXT,
                  verified BOOLEAN, languages TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Cases table
    c.execute('''CREATE TABLE IF NOT EXISTS cases
                 (id INTEGER PRIMARY KEY, user_id INTEGER, lawyer_id INTEGER,
                  title TEXT, description TEXT, category TEXT,
                  status TEXT, priority TEXT, created_at TIMESTAMP,
                  next_hearing TEXT, documents TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  FOREIGN KEY(lawyer_id) REFERENCES lawyers(id))''')
    
    # Consultations table
    c.execute('''CREATE TABLE IF NOT EXISTS consultations
                 (id INTEGER PRIMARY KEY, user_id INTEGER, lawyer_id INTEGER,
                  consultation_type TEXT, status TEXT, scheduled_at TIMESTAMP,
                  notes TEXT, fee REAL,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  FOREIGN KEY(lawyer_id) REFERENCES lawyers(id))''')
    
    # Chat messages table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_messages
                 (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT,
                  response TEXT, language TEXT, category TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

# Initialize session state
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = sqlite3.connect('legal_aid.db')
    c = conn.cursor()
    c.execute("SELECT id, user_type FROM users WHERE username=? AND password=?", 
              (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

def register_user(username, password, email, phone, location, language, user_type):
    conn = sqlite3.connect('legal_aid.db')
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO users (username, password, email, phone, location, language, user_type)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                  (username, hash_password(password), email, phone, location, language, user_type))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

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
        },
        "Hindi": {
            "fir": "FIR दर्ज करने के लिए: 1) नजदीकी पुलिस स्टेशन जाएं, 2) घटना का विवरण दें, 3) FIR की कॉपी और नंबर लें, 4) भविष्य के लिए सुरक्षित रखें। आपको किसी भी संज्ञेय अपराध के लिए FIR दर्ज करने का अधिकार है।",
            "bail": "जमानत मुकदमे के दौरान आरोपी की अस्थायी रिहाई है। प्रकार: नियमित जमानत, अग्रिम जमानत, अंतरिम जमानत। अपने मामले के लिए वकील से सलाह लें।",
            "divorce": "भारत में तलाक दाखिल किया जा सकता है: 1) हिंदू विवाह अधिनियम, 2) भारतीय ईसाई विवाह अधिनियम, 3) विशेष विवाह अधिनियम के तहत। आधार में क्रूरता, परित्याग, धर्म परिवर्तन आदि शामिल हैं।",
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
    conn = sqlite3.connect('legal_aid.db')
    c = conn.cursor()
    
    # Check if sample lawyers exist
    c.execute("SELECT COUNT(*) FROM lawyers")
    if c.fetchone()[0] == 0:
        sample_lawyers = [
            ("Advocate Priya Sharma", "priya.sharma@email.com", "+91-9876543210", "Family Law", 8, "Mumbai", 4.5, "₹500-2000", True, "English, Hindi, Marathi"),
            ("Advocate Rajesh Kumar", "rajesh.kumar@email.com", "+91-9876543211", "Criminal Law", 12, "Delhi", 4.7, "₹1000-3000", True, "English, Hindi"),
            ("Advocate Meera Nair", "meera.nair@email.com", "+91-9876543212", "Property Law", 6, "Bangalore", 4.3, "₹800-2500", True, "English, Hindi, Tamil"),
            ("Advocate Arjun Singh", "arjun.singh@email.com", "+91-9876543213", "Consumer Rights", 5, "Chennai", 4.2, "₹300-1500", True, "English, Hindi, Telugu"),
            ("Advocate Kavita Patel", "kavita.patel@email.com", "+91-9876543214", "Employment Law", 10, "Pune", 4.6, "₹600-2000", True, "English, Hindi, Gujarati")
        ]
        
        for lawyer in sample_lawyers:
            c.execute("""INSERT INTO lawyers (name, email, phone, specialization, experience, 
                         location, rating, fee_range, verified, languages) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", lawyer)
    
    conn.commit()
    conn.close()

# Main application pages
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
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>👨‍⚖️ Find Lawyers</h3>
            <p>Connect with verified lawyers for consultation and representation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📋 Track Cases</h3>
            <p>Monitor your case progress and important deadlines</p>
        </div>
        """, unsafe_allow_html=True)
    
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
            for sender, message in st.session_state.chat_history[-10:]:  # Show last 10 messages
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
                conn = sqlite3.connect('legal_aid.db')
                c = conn.cursor()
                c.execute("INSERT INTO chat_messages (user_id, message, response, language) VALUES (?, ?, ?, ?)",
                         (st.session_state.user_id, user_input, response, language))
                conn.commit()
                conn.close()
            
            st.rerun()

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
    
    # Get lawyers from database
    conn = sqlite3.connect('legal_aid.db')
    query = "SELECT * FROM lawyers WHERE verified = 1"
    params = []
    
    if specialization_filter != "All":
        query += " AND specialization = ?"
        params.append(specialization_filter)
    if location_filter != "All":
        query += " AND location = ?"
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
                        # Here you would typically save the consultation request
                    else:
                        st.warning("Please login to book consultation")
            
            with col2:
                if st.button(f"View Profile", key=f"profile_{lawyer['id']}"):
                    st.info(f"Viewing profile of {lawyer['name']}")
            
            with col3:
                if st.button(f"Chat", key=f"chat_{lawyer['id']}"):
                    if st.session_state.authenticated:
                        st.info(f"Starting chat with {lawyer['name']}")
                    else:
                        st.warning("Please login to start chat")

def show_case_tracking():
    st.title("📋 Case Tracking & Management")
    
    if not st.session_state.authenticated:
        st.warning("Please login to access case tracking")
        return
    
    # Get user cases
    conn = sqlite3.connect('legal_aid.db')
    cases_df = pd.read_sql_query("""
        SELECT c.*, l.name as lawyer_name 
        FROM cases c 
        LEFT JOIN lawyers l ON c.lawyer_id = l.id 
        WHERE c.user_id = ?
    """, conn, params=[st.session_state.user_id])
    conn.close()
    
    # Add new case
    with st.expander("➕ Add New Case"):
        with st.form("new_case_form"):
            case_title = st.text_input("Case Title")
            case_description = st.text_area("Case Description")
            case_category = st.selectbox("Category", 
                ["Family Law", "Criminal Law", "Property Law", "Consumer Rights", "Employment Law"])
            case_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
            
            if st.form_submit_button("Create Case"):
                conn = sqlite3.connect('legal_aid.db')
                c = conn.cursor()
                c.execute("""INSERT INTO cases (user_id, title, description, category, status, priority, created_at)
                             VALUES (?, ?, ?, ?, 'Open', ?, ?)""",
                         (st.session_state.user_id, case_title, case_description, case_category, case_priority, datetime.now()))
                conn.commit()
                conn.close()
                st.success("Case created successfully!")
                st.rerun()
    
    # Display existing cases
    if cases_df.empty:
        st.info("No cases found. Create your first case above.")
    else:
        for idx, case in cases_df.iterrows():
            status_class = f"status-{case['status'].lower()}" if pd.notna(case['status']) else "status-pending"
            
            st.markdown(f"""
            <div class="feature-card">
                <h4>{case['title']} <span class="case-status {status_class}">{case['status'] or 'Pending'}</span></h4>
                <p><strong>Category:</strong> {case['category']} | <strong>Priority:</strong> {case['priority']}</p>
                <p><strong>Description:</strong> {case['description']}</p>
                <p><strong>Lawyer:</strong> {case['lawyer_name'] or 'Not assigned'}</p>
                <p><strong>Created:</strong> {case['created_at']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Update Status", key=f"update_{case['id']}"):
                    st.info("Status update feature - to be implemented")
            with col2:
                if st.button(f"Upload Documents", key=f"docs_{case['id']}"):
                    st.info("Document upload feature - to be implemented")
            with col3:
                if st.button(f"View Details", key=f"details_{case['id']}"):
                    st.info("Detailed case view - to be implemented")

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

def show_login_page():
    st.title("🔐 Login / Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                result = authenticate_user(username, password)
                if result:
                    st.session_state.authenticated = True
                    st.session_state.user_id = result[0]
                    st.session_state.user_type = result[1]
                    st.session_state.current_page = "Home"  # Redirect to home after login
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            location = st.selectbox("Location", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Other"])
            language = st.selectbox("Preferred Language", ["English", "Hindi", "Tamil", "Telugu", "Bengali", "Malayalam"])
            user_type = st.selectbox("Account Type", ["Citizen", "Lawyer", "Legal Aid Worker"])
            
            if st.form_submit_button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if register_user(new_username, new_password, email, phone, location, language, user_type):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists")

# Main application logic
def main():
    init_database()
    init_session_state()
    init_sample_data()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    if st.session_state.authenticated:
        st.sidebar.success(f"Welcome! User ID: {st.session_state.user_id}")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_type = None
            st.session_state.chat_history = []
            st.session_state.current_page = "Home"  # Reset to home page
            st.rerun()
    
    # Navigation menu - dynamic based on authentication
    if st.session_state.authenticated:
        pages = {
            "🏠 Home": "Home",
            "🤖 Legal Chatbot": "Chatbot",
            "👨‍⚖️ Find Lawyers": "Lawyers",
            "📋 Case Tracking": "Cases",
            "📖 Legal Awareness": "Awareness"
        }
    else:
        pages = {
            "🏠 Home": "Home",
            "🤖 Legal Chatbot": "Chatbot",
            "👨‍⚖️ Find Lawyers": "Lawyers",
            "📖 Legal Awareness": "Awareness",
            "🔐 Login": "Login"
        }
    
    # Use radio buttons for better navigation experience
    selected_page = st.sidebar.radio("Go to", list(pages.keys()), 
                                    index=list(pages.values()).index(st.session_state.current_page) 
                                    if st.session_state.current_page in pages.values() else 0)
    
    # Update current page based on selection
    new_page = pages[selected_page]
    if new_page != st.session_state.current_page:
        st.session_state.current_page = new_page
        st.rerun()
    
    # Route to appropriate page
    if st.session_state.current_page == "Home":
        show_home_page()
    elif st.session_state.current_page == "Chatbot":
        show_chatbot_page()
    elif st.session_state.current_page == "Lawyers":
        show_lawyer_marketplace()
    elif st.session_state.current_page == "Cases":
        show_case_tracking()
    elif st.session_state.current_page == "Awareness":
        show_legal_awareness()
    elif st.session_state.current_page == "Login":
        show_login_page()
    
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
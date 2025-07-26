
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import base64
import io

def add_document_management():
    """Enhanced document management system"""
    st.title("📄 Document Management")
    
    if not st.session_state.authenticated:
        st.warning("Please login to access document management")
        return
    
    tabs = st.tabs(["Upload Documents", "My Documents", "Document Templates"])
    
    with tabs[0]:
        st.subheader("Upload Legal Documents")
        
        document_type = st.selectbox("Document Type", [
            "Affidavit", "FIR Copy", "Court Order", "Property Papers", 
            "Employment Contract", "Marriage Certificate", "Other"
        ])
        
        case_id = st.selectbox("Associate with Case", ["None", "Case 1", "Case 2"])  # This would be dynamic
        
        uploaded_file = st.file_uploader(
            "Choose file", 
            type=['pdf', 'doc', 'docx', 'jpg', 'png'],
            help="Supported formats: PDF, DOC, DOCX, JPG, PNG"
        )
        
        if uploaded_file:
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            
            # In a real application, you would save this to a secure file storage
            # and store metadata in the database
            
    with tabs[1]:
        st.subheader("Your Documents")
        
        # Sample document data - in real app, fetch from database
        documents_data = {
            'Document': ['Affidavit_Property.pdf', 'FIR_Copy.pdf', 'Marriage_Certificate.jpg'],
            'Type': ['Affidavit', 'FIR Copy', 'Marriage Certificate'],
            'Upload Date': ['2024-01-15', '2024-01-10', '2024-01-05'],
            'Case': ['Property Dispute', 'Theft Case', 'None'],
            'Status': ['Verified', 'Pending', 'Verified']
        }
        
        df = pd.DataFrame(documents_data)
        st.dataframe(df)
        
        # Document actions
        for idx, doc in df.iterrows():
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"View {doc['Document']}", key=f"view_{idx}"):
                    st.info(f"Viewing {doc['Document']}")
            with col2:
                if st.button(f"Share {doc['Document']}", key=f"share_{idx}"):
                    st.info(f"Sharing {doc['Document']} with lawyer")
            with col3:
                if st.button(f"Delete {doc['Document']}", key=f"delete_{idx}"):
                    st.warning(f"Delete confirmation for {doc['Document']}")
    
    with tabs[2]:
        st.subheader("Document Templates")
        
        templates = {
            "Affidavit Template": "Standard affidavit format for legal proceedings",
            "RTI Application": "Right to Information application template",
            "Consumer Complaint": "Consumer forum complaint format",
            "Bail Application": "Bail application template",
            "Divorce Petition": "Mutual consent divorce petition format"
        }
        
        for template, description in templates.items():
            with st.expander(template):
                st.write(description)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Download {template}", key=f"download_{template}"):
                        st.success(f"Downloading {template}")
                with col2:
                    if st.button(f"Fill Online {template}", key=f"fill_{template}"):
                        st.info(f"Opening form for {template}")

def add_appointment_system():
    """Enhanced appointment scheduling system"""
    st.title("📅 Appointment Scheduling")
    
    if not st.session_state.authenticated:
        st.warning("Please login to schedule appointments")
        return
    
    tabs = st.tabs(["Book Appointment", "My Appointments", "Calendar View"])
    
    with tabs[0]:
        st.subheader("Book New Appointment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lawyer_name = st.selectbox("Select Lawyer", [
                "Advocate Priya Sharma", "Advocate Rajesh Kumar", 
                "Advocate Meera Nair", "Advocate Arjun Singh"
            ])
            
            appointment_type = st.selectbox("Appointment Type", [
                "Initial Consultation", "Case Discussion", "Document Review", 
                "Court Preparation", "Follow-up Meeting"
            ])
            
            appointment_date = st.date_input("Preferred Date", 
                                           min_value=datetime.today().date())
        
        with col2:
            appointment_time = st.time_input("Preferred Time")
            
            meeting_mode = st.selectbox("Meeting Mode", [
                "In-Person", "Video Call", "Phone Call"
            ])
            
            urgency = st.selectbox("Urgency Level", [
                "Normal", "Urgent", "Emergency"
            ])
        
        description = st.text_area("Describe your legal issue", 
                                 placeholder="Please provide details about your case...")
        
        if st.button("Book Appointment"):
            st.success(f"""
            Appointment booked successfully!
            
            **Details:**
            - Lawyer: {lawyer_name}
            - Date: {appointment_date}
            - Time: {appointment_time}
            - Mode: {meeting_mode}
            - Type: {appointment_type}
            
            You will receive a confirmation message shortly.
            """)
    
    with tabs[1]:
        st.subheader("Your Appointments")
        
        # Sample appointment data
        appointments_data = {
            'Lawyer': ['Advocate Priya Sharma', 'Advocate Rajesh Kumar', 'Advocate Meera Nair'],
            'Date': ['2024-02-15', '2024-02-18', '2024-02-22'],
            'Time': ['10:00 AM', '2:30 PM', '11:15 AM'],
            'Type': ['Initial Consultation', 'Case Discussion', 'Document Review'],
            'Mode': ['Video Call', 'In-Person', 'Phone Call'],
            'Status': ['Confirmed', 'Pending', 'Confirmed']
        }
        
        df = pd.DataFrame(appointments_data)
        
        for idx, apt in df.iterrows():
            status_color = "green" if apt['Status'] == 'Confirmed' else "orange"
            
            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                <h4 style="margin: 0;">{apt['Lawyer']} 
                <span style="color: {status_color}; font-size: 0.8em;">● {apt['Status']}</span></h4>
                <p><strong>📅 {apt['Date']} at {apt['Time']}</strong></p>
                <p>📞 {apt['Mode']} | 📋 {apt['Type']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Reschedule", key=f"reschedule_{idx}"):
                    st.info("Rescheduling feature")
            with col2:
                if st.button(f"Cancel", key=f"cancel_{idx}"):
                    st.warning("Cancellation confirmation")
            with col3:
                if st.button(f"Join Meeting", key=f"join_{idx}"):
                    st.success("Joining meeting...")
    
    with tabs[2]:
        st.subheader("Calendar View")
        
        # Create a simple calendar visualization
        dates = pd.date_range(start='2024-02-01', end='2024-02-29', freq='D')
        appointments = [1, 0, 0, 2, 0, 1, 0] * 4  # Sample data
        
        calendar_data = pd.DataFrame({
            'Date': dates[:len(appointments)],
            'Appointments': appointments
        })
        
        fig = px.calendar(calendar_data, x='Date', y='Appointments', 
                         title="Your Appointment Calendar")
        st.plotly_chart(fig)

def add_payment_system():
    """Payment integration for lawyer consultations"""
    st.title("💳 Payment & Billing")
    
    if not st.session_state.authenticated:
        st.warning("Please login to access payment features")
        return
    
    tabs = st.tabs(["Make Payment", "Payment History", "Billing"])
    
    with tabs[0]:
        st.subheader("Make Payment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            payment_for = st.selectbox("Payment For", [
                "Consultation Fee", "Case Handling Fee", "Document Review", 
                "Court Representation", "Legal Advice"
            ])
            
            lawyer_name = st.selectbox("Lawyer", [
                "Advocate Priya Sharma (₹1500)", 
                "Advocate Rajesh Kumar (₹2000)",
                "Advocate Meera Nair (₹1200)"
            ])
            
            amount = st.number_input("Amount (₹)", min_value=100, value=1500)
        
        with col2:
            payment_method = st.selectbox("Payment Method", [
                "UPI", "Credit/Debit Card", "Net Banking", "Digital Wallet"
            ])
            
            if payment_method == "UPI":
                upi_id = st.text_input("UPI ID", placeholder="yourname@paytm")
            elif payment_method == "Credit/Debit Card":
                card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
                col2a, col2b = st.columns(2)
                with col2a:
                    expiry = st.text_input("MM/YY", placeholder="12/25")
                with col2b:
                    cvv = st.text_input("CVV", placeholder="123", type="password")
        
        # Payment summary
        st.markdown("---")
        st.subheader("Payment Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Service:** {payment_for}")
            st.write(f"**Lawyer:** {lawyer_name.split('(')[0]}")
            st.write(f"**Amount:** ₹{amount}")
        
        with col2:
            st.write(f"**GST (18%):** ₹{amount * 0.18:.2f}")
            st.write(f"**Total Amount:** ₹{amount * 1.18:.2f}")
        
        if st.button("Proceed to Payment", type="primary"):
            st.success("""
            🎉 Payment Successful!
            
            **Transaction ID:** TXN123456789
            **Amount Paid:** ₹{:.2f}
            **Status:** Completed
            
            A receipt has been sent to your email.
            """.format(amount * 1.18))
    
    with tabs[1]:
        st.subheader("Payment History")
        
        payment_history = {
            'Date': ['2024-01-20', '2024-01-15', '2024-01-10'],
            'Lawyer': ['Advocate Priya Sharma', 'Advocate Rajesh Kumar', 'Advocate Meera Nair'],
            'Service': ['Consultation', 'Case Handling', 'Document Review'],
            'Amount': ['₹1770', '₹2360', '₹1416'],
            'Status': ['Completed', 'Completed', 'Completed'],
            'Receipt': ['Download', 'Download', 'Download']
        }
        
        df = pd.DataFrame(payment_history)
        st.dataframe(df)
        
        # Payment analytics
        st.subheader("Spending Analytics")
        
        spending_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Amount': [5500, 3200, 4100, 2800, 3600]
        })
        
        fig = px.bar(spending_data, x='Month', y='Amount', 
                    title='Monthly Legal Expenses')
        st.plotly_chart(fig)
    
    with tabs[2]:
        st.subheader("Billing & Invoices")
        
        st.info("📧 All invoices are automatically sent to your registered email address.")
        
        # Pending bills
        pending_bills = {
            'Invoice #': ['INV-001', 'INV-002'],
            'Lawyer': ['Advocate Priya Sharma', 'Advocate Rajesh Kumar'],
            'Service': ['Ongoing Case', 'Consultation'],
            'Amount': ['₹5000', '₹1500'],
            'Due Date': ['2024-02-28', '2024-02-25'],
            'Status': ['Pending', 'Overdue']
        }
        
        pending_df = pd.DataFrame(pending_bills)
        
        st.markdown("**Pending Bills:**")
        st.dataframe(pending_df)
        
        # Quick payment buttons
        for idx, bill in pending_df.iterrows():
            if st.button(f"Pay {bill['Invoice #']} - {bill['Amount']}", key=f"pay_{idx}"):
                st.success(f"Redirecting to payment for {bill['Invoice #']}")

def add_legal_news_feed():
    """Legal news and updates feed"""
    st.title("📰 Legal News & Updates")
    
    # Sample news data - in production, this would come from RSS feeds or news APIs
    news_data = [
        {
            'title': 'Supreme Court Ruling on Digital Privacy Rights',
            'summary': 'The Supreme Court has issued new guidelines on digital privacy...',
            'category': 'Constitutional Law',
            'date': '2024-02-10',
            'source': 'Legal Tribune India'
        },
        {
            'title': 'New Consumer Protection Guidelines Released',
            'summary': 'The Ministry of Consumer Affairs has released updated guidelines...',
            'category': 'Consumer Law',
            'date': '2024-02-08',
            'source': 'Consumer Rights Weekly'
        },
        {
            'title': 'Changes in Property Registration Process',
            'summary': 'State governments are implementing digital property registration...',
            'category': 'Property Law',
            'date': '2024-02-05',
            'source': 'Property Legal News'
        }
    ]
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox("Filter by Category", 
            ["All", "Constitutional Law", "Consumer Law", "Property Law", "Criminal Law"])
    with col2:
        date_filter = st.selectbox("Filter by Date", 
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 3 Months"])
    
    # Display news
    for news in news_data:
        if category_filter == "All" or news['category'] == category_filter:
            with st.expander(f"📰 {news['title']} - {news['date']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Category:** {news['category']}")
                    st.write(news['summary'])
                    st.write(f"**Source:** {news['source']}")
                with col2:
                    if st.button("Read Full Article", key=f"read_{news['title']}"):
                        st.info("Opening full article...")
                    if st.button("Save Article", key=f"save_{news['title']}"):
                        st.success("Article saved to your reading list!")

def add_analytics_dashboard():
    """Analytics dashboard for admin users"""
    st.title("📊 Analytics Dashboard")
    
    if st.session_state.user_type != "Legal Aid Worker":
        st.warning("Access restricted to Legal Aid Workers only")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "1,250", "+12%")
    with col2:
        st.metric("Active Cases", "340", "+5%")
    with col3:
        st.metric("Consultations", "89", "+18%")
    with col4:
        st.metric("Resolution Rate", "78%", "+3%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # User growth chart
        user_growth_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'New Users': [45, 67, 89, 123, 156, 189],
            'Total Users': [450, 517, 606, 729, 885, 1074]
        })
        
        fig = px.line(user_growth_data, x='Month', y=['New Users', 'Total Users'], 
                     title='User Growth Trend')
        st.plotly_chart(fig)
    
    with col2:
        # Case distribution by type
        case_types = pd.DataFrame({
            'Type': ['Family Law', 'Criminal Law', 'Property Law', 'Consumer Rights', 'Employment'],
            'Count': [125, 89, 67, 34, 25]
        })
        
        fig = px.pie(case_types, values='Count', names='Type', 
                    title='Cases by Category')
        st.plotly_chart(fig)
    
    # Detailed tables
    st.subheader("Recent Activity")
    
    activity_data = {
        'Time': ['10:30 AM', '10:15 AM', '09:45 AM', '09:30 AM'],
        'User': ['User123', 'User456', 'User789', 'User101'],
        'Action': ['Case Created', 'Consultation Booked', 'Document Uploaded', 'Payment Made'],
        'Details': ['Property Dispute', 'Divorce Consultation', 'Affidavit.pdf', '₹1500']
    }
    
    st.dataframe(pd.DataFrame(activity_data))

# Export functions for main app integration
def get_enhanced_features():
    """Return dictionary of enhanced features"""
    return {
        "Document Management": add_document_management,
        "Appointment System": add_appointment_system,
        "Payment System": add_payment_system,
        "Legal News": add_legal_news_feed,
        "Analytics Dashboard": add_analytics_dashboard
    }
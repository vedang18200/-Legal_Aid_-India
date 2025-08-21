import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the application"""
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

# Status color mappings
STATUS_COLORS = {
    'Open': '#28a745',
    'In Progress': '#17a2b8',
    'Closed': '#6c757d',
    'Pending': '#ffc107',
    'On Hold': '#fd7e14',
    'Cancelled': '#dc3545',
    'Completed': '#28a745',
    'Scheduled': '#17a2b8'
}

# Priority color mappings
PRIORITY_COLORS = {
    'Low': '#28a745',
    'Medium': '#ffc107',
    'High': '#fd7e14',
    'Urgent': '#dc3545'
}

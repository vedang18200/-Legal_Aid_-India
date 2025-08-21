import streamlit as st
import psycopg2
import pandas as pd
from config.settings import DB_CONFIG

def get_pg_connection():
    """Create a new PostgreSQL connection"""
    try:
        return psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=st.secrets[DB_CONFIG["password_key"]]
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

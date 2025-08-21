import streamlit as st
from database.db_manager import execute_query
from datetime import datetime

def send_message(sender_id, receiver_id, message):
    """Send a direct message between users with better error handling"""
    try:
        execute_query(
            """INSERT INTO direct_messages (sender_id, receiver_id, message, sent_at, read_at)
               VALUES (%s, %s, %s, NOW(), NULL)""",
            (sender_id, receiver_id, message)
        )
        return True
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return False

def get_unread_message_count(user_id):
    """Get count of unread messages for a user"""
    try:
        count = execute_query(
            "SELECT COUNT(*) FROM direct_messages WHERE receiver_id = %s AND read_at IS NULL",
            (user_id,),
            fetch='one'
        )
        return count[0] if count else 0
    except Exception as e:
        st.error(f"Error getting unread count: {e}")
        return 0

def get_messages(user1_id, user2_id, limit=50):
    """Get all messages between two users with pagination"""
    try:
        messages = execute_query(
            """SELECT sender_id, receiver_id, message, sent_at, read_at
               FROM direct_messages
               WHERE (sender_id = %s AND receiver_id = %s)
                  OR (sender_id = %s AND receiver_id = %s)
               ORDER BY sent_at ASC
               LIMIT %s""",
            (user1_id, user2_id, user2_id, user1_id, limit),
            fetch='all'
        )

        # Mark messages as read for the current user
        mark_messages_as_read(user2_id, user1_id)

        return messages if messages else []
    except Exception as e:
        st.error(f"Error fetching messages: {e}")
        return []

def get_user_conversations(user_id):
    """Get all conversations for a specific user with enhanced data"""
    try:
        conversations = execute_query(
            """SELECT DISTINCT
                   CASE
                       WHEN sender_id = %s THEN receiver_id
                       ELSE sender_id
                   END as other_user_id,
                   u.username as other_username,
                   u.user_type as other_user_type,
                   MAX(dm.sent_at) as last_message_time,
                   (SELECT message FROM direct_messages dm2
                    WHERE (dm2.sender_id = %s AND dm2.receiver_id = CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END)
                       OR (dm2.receiver_id = %s AND dm2.sender_id = CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END)
                    ORDER BY dm2.sent_at DESC LIMIT 1) as last_message,
                   (SELECT COUNT(*) FROM direct_messages dm3
                    WHERE dm3.sender_id = CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END
                    AND dm3.receiver_id = %s AND dm3.read_at IS NULL) as unread_count
               FROM direct_messages dm
               JOIN users u
                 ON u.id = CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END
               WHERE sender_id = %s OR receiver_id = %s
               GROUP BY other_user_id, u.username, u.user_type
               ORDER BY last_message_time DESC""",
            (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id),
            fetch='all'
        )
        return conversations if conversations else []
    except Exception as e:
        st.error(f"Error fetching conversations: {e}")
        return []

def mark_messages_as_read(sender_id, receiver_id):
    """Mark messages as read"""
    try:
        execute_query(
            """UPDATE direct_messages
               SET read_at = NOW()
               WHERE sender_id = %s AND receiver_id = %s AND read_at IS NULL""",
            (sender_id, receiver_id)
        )
        return True
    except Exception as e:
        st.error(f"Error marking messages as read: {e}")
        return False

def create_appointment_request(client_id, lawyer_id, appointment_date, appointment_time,
                             appointment_type, meeting_method, duration, notes=""):
    """Create an appointment request"""
    try:
        execute_query(
            """INSERT INTO appointments (client_id, lawyer_id, appointment_date,
               appointment_time, appointment_type, meeting_method, duration,
               notes, status, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
            (client_id, lawyer_id, appointment_date, appointment_time,
             appointment_type, meeting_method, duration, notes, 'pending')
        )
        return True
    except Exception as e:
        st.error(f"Error creating appointment: {e}")
        return False

def get_user_appointments(user_id, user_type):
    """Get appointments for a user (client or lawyer)"""
    try:
        if user_type == 'lawyer':
            appointments = execute_query(
                """SELECT a.*, u.username as client_name, u.email as client_email
                   FROM appointments a
                   JOIN users u ON a.client_id = u.id
                   WHERE a.lawyer_id = (SELECT id FROM lawyers WHERE user_id = %s)
                   ORDER BY a.appointment_date DESC, a.appointment_time DESC""",
                (user_id,), fetch='all'
            )
        else:
            appointments = execute_query(
                """SELECT a.*, l.name as lawyer_name, l.email as lawyer_email
                   FROM appointments a
                   JOIN lawyers l ON a.lawyer_id = l.id
                   WHERE a.client_id = %s
                   ORDER BY a.appointment_date DESC, a.appointment_time DESC""",
                (user_id,), fetch='all'
            )

        return appointments if appointments else []
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []

def update_appointment_status(appointment_id, status, notes=""):
    """Update appointment status"""
    try:
        execute_query(
            """UPDATE appointments
               SET status = %s, response_notes = %s, updated_at = NOW()
               WHERE id = %s""",
            (status, notes, appointment_id)
        )
        return True
    except Exception as e:
        st.error(f"Error updating appointment: {e}")
        return False

def search_message_history(user1_id, user2_id, search_term):
    """Search through message history"""
    try:
        messages = execute_query(
            """SELECT sender_id, receiver_id, message, sent_at
               FROM direct_messages
               WHERE ((sender_id = %s AND receiver_id = %s)
                     OR (sender_id = %s AND receiver_id = %s))
               AND message ILIKE %s
               ORDER BY sent_at DESC
               LIMIT 20""",
            (user1_id, user2_id, user2_id, user1_id, f"%{search_term}%"),
            fetch='all'
        )
        return messages if messages else []
    except Exception as e:
        st.error(f"Error searching messages: {e}")
        return []

def get_conversation_stats(user_id):
    """Get conversation statistics for a user"""
    try:
        stats = execute_query(
            """SELECT
                COUNT(DISTINCT CASE WHEN sender_id = %s THEN receiver_id ELSE sender_id END) as total_conversations,
                COUNT(*) as total_messages,
                COUNT(CASE WHEN read_at IS NULL AND receiver_id = %s THEN 1 END) as unread_messages
               FROM direct_messages
               WHERE sender_id = %s OR receiver_id = %s""",
            (user_id, user_id, user_id, user_id),
            fetch='one'
        )
        return stats if stats else (0, 0, 0)
    except Exception as e:
        st.error(f"Error getting conversation stats: {e}")
        return (0, 0, 0)

def delete_message(message_id, user_id):
    """Delete a message (only sender can delete)"""
    try:
        result = execute_query(
            """DELETE FROM direct_messages
               WHERE id = %s AND sender_id = %s""",
            (message_id, user_id)
        )
        return True
    except Exception as e:
        st.error(f"Error deleting message: {e}")
        return False

def block_user(blocker_id, blocked_id):
    """Block a user from sending messages"""
    try:
        execute_query(
            """INSERT INTO blocked_users (blocker_id, blocked_id, created_at)
               VALUES (%s, %s, NOW())
               ON CONFLICT (blocker_id, blocked_id) DO NOTHING""",
            (blocker_id, blocked_id)
        )
        return True
    except Exception as e:
        st.error(f"Error blocking user: {e}")
        return False

def is_user_blocked(sender_id, receiver_id):
    """Check if user is blocked"""
    try:
        result = execute_query(
            """SELECT id FROM blocked_users
               WHERE blocker_id = %s AND blocked_id = %s""",
            (receiver_id, sender_id),
            fetch='one'
        )
        return result is not None
    except Exception as e:
        return False

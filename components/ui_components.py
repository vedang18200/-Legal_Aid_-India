import streamlit as st
from config.styles import STATUS_COLORS, PRIORITY_COLORS

def render_status_badge(status):
    """Render a status badge with appropriate color"""
    color = STATUS_COLORS.get(status, '#6c757d')
    return f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{status}</span>'

def render_priority_badge(priority):
    """Render a priority badge with appropriate color"""
    color = PRIORITY_COLORS.get(priority, '#6c757d')
    return f'<span style="background-color: {color}; color: white; padding: 3px 8px; border-radius: 15px; font-size: 12px;">{priority}</span>'

def render_card(title, content, card_type="default"):
    """Render a styled card component"""
    card_classes = {
        "default": "feature-card",
        "lawyer": "lawyer-card",
        "case": "feature-card"
    }

    card_class = card_classes.get(card_type, "feature-card")

    st.markdown(f"""
    <div class="{card_class}">
        <h4>{title}</h4>
        {content}
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, delta=None, delta_color="normal"):
    """Render a metric card with optional delta"""
    col = st.container()
    with col:
        if delta:
            st.metric(title, value, delta, delta_color=delta_color)
        else:
            st.metric(title, value)

def render_user_info_card(user_data):
    """Render user information card"""
    name = user_data.get('name', user_data.get('username', 'Unknown'))
    email = user_data.get('email', 'Not provided')
    phone = user_data.get('phone', 'Not provided')
    location = user_data.get('location', 'Not specified')

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #212529;">
        <h4>👤 {name}</h4>
        <p><strong>📧 Email:</strong> {email}</p>
        <p><strong>📱 Phone:</strong> {phone}</p>
        <p><strong>📍 Location:</strong> {location}</p>
    </div>
    """, unsafe_allow_html=True)

def render_case_card(case_data, show_actions=True, action_callbacks=None):
    """Render a case information card with optional actions"""
    case_id = case_data[0]
    title = case_data[3] if len(case_data) > 3 else "Unknown Case"
    description = case_data[4] if len(case_data) > 4 else "No description"
    category = case_data[5] if len(case_data) > 5 else "General"
    status = case_data[6] if len(case_data) > 6 else "Unknown"
    priority = case_data[7] if len(case_data) > 7 else "Medium"

    status_badge = render_status_badge(status)
    priority_badge = render_priority_badge(priority)

    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 10px; background-color: #212529;">
        <h4>{title} {status_badge}</h4>
        <p><strong>Category:</strong> {category} | <strong>Priority:</strong> {priority_badge}</p>
        <p><strong>Description:</strong> {description}</p>
    </div>
    """, unsafe_allow_html=True)

    if show_actions and action_callbacks:
        cols = st.columns(len(action_callbacks))
        for i, (label, callback) in enumerate(action_callbacks.items()):
            with cols[i]:
                if st.button(label, key=f"{label}_{case_id}"):
                    callback(case_id)

def render_lawyer_card(lawyer_data, show_actions=True, action_callbacks=None):
    """Render a lawyer information card with optional actions"""
    lawyer_id = lawyer_data.get('id') if isinstance(lawyer_data, dict) else lawyer_data[0]
    name = lawyer_data.get('name') if isinstance(lawyer_data, dict) else lawyer_data[1]
    specialization = lawyer_data.get('specialization') if isinstance(lawyer_data, dict) else lawyer_data[4]
    experience = lawyer_data.get('experience') if isinstance(lawyer_data, dict) else lawyer_data[5]
    location = lawyer_data.get('location') if isinstance(lawyer_data, dict) else lawyer_data[6]
    rating = lawyer_data.get('rating') if isinstance(lawyer_data, dict) else lawyer_data[7]
    fee_range = lawyer_data.get('fee_range') if isinstance(lawyer_data, dict) else lawyer_data[8]
    languages = lawyer_data.get('languages') if isinstance(lawyer_data, dict) else lawyer_data[10]

    st.markdown(f"""
    <div class="lawyer-card">
        <h4>{name} ⭐ {rating}/5.0</h4>
        <p><strong>Specialization:</strong> {specialization} |
           <strong>Experience:</strong> {experience} years |
           <strong>Location:</strong> {location}</p>
        <p><strong>Fee Range:</strong> {fee_range} |
           <strong>Languages:</strong> {languages}</p>
    </div>
    """, unsafe_allow_html=True)

    if show_actions and action_callbacks:
        cols = st.columns(len(action_callbacks))
        for i, (label, callback) in enumerate(action_callbacks.items()):
            with cols[i]:
                if st.button(label, key=f"{label}_{lawyer_id}"):
                    callback(lawyer_data)

def render_confirmation_dialog(message, confirm_callback, cancel_callback=None):
    """Render a confirmation dialog"""
    st.warning(message)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Confirm", type="primary"):
            confirm_callback()

    with col2:
        if st.button("❌ Cancel"):
            if cancel_callback:
                cancel_callback()
            else:
                st.rerun()

def render_loading_spinner(message="Loading..."):
    """Render a loading spinner with message"""
    with st.spinner(message):
        return st.empty()

def render_success_message(message, auto_disappear=False):
    """Render a success message"""
    if auto_disappear:
        placeholder = st.empty()
        placeholder.success(message)
        return placeholder
    else:
        st.success(message)

def render_error_message(message):
    """Render an error message"""
    st.error(message)

def render_info_message(message):
    """Render an info message"""
    st.info(message)

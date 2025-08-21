import streamlit as st

def show_legal_awareness():
    """Display legal awareness portal"""
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

    # Emergency contacts
    with st.expander("🚨 Emergency Legal Contacts"):
        st.markdown("""
        ### Important Helpline Numbers:
        - **Emergency Legal Helpline**: 1800-345-4357
        - **NALSA Helpline**: 15100
        - **Women Helpline**: 1091
        - **Cyber Crime Helpline**: 1930
        - **Child Helpline**: 1098
        - **Police**: 100
        - **Ambulance**: 108
        """)

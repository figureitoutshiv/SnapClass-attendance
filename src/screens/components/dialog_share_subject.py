import streamlit as st
from src.screens.database.db import create_subject, get_teacher_subjects
import segno
import io

@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    app_domain = "http://localhost:8501/"
    join_url = f"{app_domain}?join-code={subject_code}"

    st.header(f"Scan the QR code or share the link below to invite students to join the class '{subject_name}'.")

    qr = segno.make(join_url)

    out = io.BytesIO()
    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.header('Copy Link')
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info('Copy this link to share on Whatsapp or Email')

    with col2:
        st.header('Scan to Join')
        st.image(out.getvalue(), caption='QRCODE for class joining')

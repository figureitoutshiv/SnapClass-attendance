import streamlit as st
from PIL import Image
from src.screens.database.db import create_subject
from src.screens.database.db import create_attendance

@st.dialog("Attendance Results", width="stretch")

def attendance_result_dialog(df, logs):
    st.write('please review attendance results below and add any missing students.')
    st.dataframe(df, hide_index=True, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard', width="stretch"):
            st.rerun()

    with col2:
        if st.button("Confirm", width="stretch"):
            try:
                 create_attendance(logs)
                 st.toast("Attendance taken")
                 st.session_state.attendance_images = []
                 st.rerun()
                 
            except Exception as e:
                    st.error(f"Error logging attendance: {e}")
                

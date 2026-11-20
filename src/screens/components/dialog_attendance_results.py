import streamlit as st
from PIL import Image
from src.screens.database.db import create_subject
from src.screens.database.db import create_attendance



def show_attendance_result(df, logs):
    st.write('please review attendance results below and add any missing students.')
    st.dataframe(df, hide_index=True, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard', width="stretch"):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_image = []
            st.rerun()

    with col2:
        if st.button("Confirm", width="stretch"):
            try:
                create_attendance(logs)
                st.toast("Attendance taken")
                st.session_state.attendance_image = []
                st.session_state.pop("voice_attendance_results", None)
                st.rerun()

            except Exception as e:
                    st.error(f"Error logging attendance: {e}")

@st.dialog("Attendance Results", width="stretch")

def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)

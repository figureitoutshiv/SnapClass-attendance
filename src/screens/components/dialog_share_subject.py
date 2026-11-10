import streamlit as st

@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    st.write(f"Share **{subject_name}** with students using this subject code:")
    st.code(subject_code)

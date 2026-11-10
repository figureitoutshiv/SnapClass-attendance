import streamlit as st
from src.screens.database.db import create_subject

@st.dialog("Create New Subject", width="stretch")

def create_subject_dialog(teacher_id):
    teacher_data = st.session_state.get("teacher_data")
    if not teacher_data or teacher_data.get("teacher_id") != teacher_id:
        st.error("You must be logged in as this teacher to create a subject.")
        return

    st.write("Enter details of the new subject below:")
    sub_id = st.text_input("Subject code", placeholder="CS101")
    sub_name = st.text_input("Subject name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")

    if st.button("Create Subject Now", type='primary', width="stretch"):

        if sub_id and sub_name and sub_section:
            try:
                create_subject(teacher_id, sub_id, sub_name, sub_section)
                st.toast(f"Subject '{sub_name}' created successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating subject: {e}")
        else:
            st.warning("Please fill in all fields.")
import streamlit as st
from src.screens.database.db import (
    enroll_student_to_subject,
    get_students_subjects,
    get_subject_by_code,
)


@st.dialog("Enroll in Subject")
def auto_enroll_dialog(join_code):
    student_id = st.session_state.student_data["student_id"]
    subject = get_subject_by_code(join_code)

    if not subject:
        st.warning("No subject found with that code.")
        if st.button("Close", type="primary", width="stretch"):
            st.query_params.clear()
            st.rerun()
        return

    subject_id = subject["subject_id"]
    enrolled_subject_ids = {
        row["subject_id"] for row in get_students_subjects(student_id)
    }
    if subject_id in enrolled_subject_ids:
        st.warning("You are already enrolled in this program.")
        if st.button("Close", type="primary", width="stretch"):
            st.query_params.clear()
            st.rerun()
        return

    st.markdown(
        f"You are about to enroll in the subject: **{subject['name']}**?"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("No", type="secondary", width="stretch"):
            st.query_params.clear()
            st.rerun()

    with col2:
        if st.button("Yes, Enroll me now", type="primary", width="stretch"):
            if enroll_student_to_subject(student_id, subject_id):
                st.session_state["_flash"] = ("Successfully enrolled!", "✅")
                st.query_params.clear()
                st.rerun()
            st.warning("You are already enrolled in this program.")
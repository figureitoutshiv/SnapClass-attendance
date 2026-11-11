import streamlit as st
from src.screens.database.db import enroll_student_to_subject, get_subject_by_code
import time


@st.dialog("Enroll in Subject")

def enroll_dialog():
    st.write('Enter the subject code provided by your teacher to enroll')
    join_code = st.text_input('Subject Code', placeholder='Eg. CS101').strip()

    if st.button('Enroll now', type='primary', width='stretch'):
        if join_code:
            subject = get_subject_by_code(join_code)
            if subject:
                student_id = st.session_state.student_data['student_id']

                enrolled = enroll_student_to_subject(
                    student_id,
                    subject['subject_id'],
                )
                if not enrolled:
                    st.warning('You are already enrolled in this program')
                else:
                    st.success('Successfully enrolled!')
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning('No subject found with that code.')

        else:
            st.warning('Please enter a subject code')
    
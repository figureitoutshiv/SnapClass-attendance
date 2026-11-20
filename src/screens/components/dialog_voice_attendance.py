import streamlit as st
from src.screens.database.db import get_subject_students
from src.screens.pipeline.voice_pipeline import process_bulk_audio
from src.screens.components.dialog_attendance_results import show_attendance_result
from datetime import datetime
import pandas as pd


@st.dialog('Voice Attendance')

def voice_attendance_dialog(selected_subject_id):
    st.write("Record Audio.")

    audio_data = None

    audio_data = st.audio_input("Record classroom audio")

    if st.button('Analyze Audio', width="stretch", type="primary"):
        with st.spinner('Processing Audio data'):
            if audio_data is None:
                st.warning("Record audio before analyzing attendance.")
                return

            teacher_id = st.session_state.teacher_data["teacher_id"]
            enrolled_students = get_subject_students(
                teacher_id, selected_subject_id
            )

            if not enrolled_students:
                st.warning('No students enrolled in this course')
                return
            canditate_dict = {
                student['student_id']: student['voice_embedding']
                for student in enrolled_students
                if student.get('voice_embedding')
            }

            if not canditate_dict:
                st.error("No enrolled student registered.")
                return

            audio_bytes = audio_data.read()

            detected_scores = process_bulk_audio(audio_bytes, canditate_dict)

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for student in enrolled_students:
                score= detected_scores.get(student['student_id'], 0.0)
                is_present = bool(score > 0)

                results.append({
                    "Name": student['name'],
                    "ID": student['student_id'],
                    "Sources": score if is_present else "_",
                    "Status": "Present" if is_present else "Absent"
                })

                attendance_to_log.append({
                    "student_id": student['student_id'],
                    "subject_id": selected_subject_id,
                    "timestamp": current_timestamp,
                    "is_present": bool(is_present)
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)
import streamlit as st
from PIL import Image
import numpy as np
import io
import time
from .components.dialog_enroll import enroll_dialog
from src.screens.components.navigation import dashboard_navigation
import src.screens.pipeline.face_pipeline
from  src.screens.pipeline.voice_pipeline import get_voice_embedding
from  src.screens.database.db import get_all_students, create_student
from src.screens.database.db import (
    get_students_attendance,
    get_students_subjects,
    unenroll_student_to_subject,
)


@st.cache_data(show_spinner=False, max_entries=16)
def _recognise(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return src.screens.pipeline.face_pipeline.predict_attendance(np.array(image))


def _flash(msg: str, icon: str = "✅"):
    st.session_state["_flash"] = (msg, icon)


def _render_flash():
    flash = st.session_state.pop("_flash", None)
    if flash:
        st.toast(flash[0], icon=flash[1])

def student_screen():
    if "student_data" in st.session_state:
        _render_flash()
        student_dashboard()
        return

    auth_mode = st.session_state.get("student_auth_mode")
    if auth_mode is None:
        st.title("Student Portal", text_alignment="center")
        st.subheader("Choose an option to continue", text_alignment="center")
        login_col, register_col = st.columns(2)
        with login_col:
            if st.button("Student Login", type="primary", width="stretch"):
                st.session_state["student_auth_mode"] = "login"
                st.rerun()
        with register_col:
            if st.button("Register", type="primary", width="stretch"):
                st.session_state["student_auth_mode"] = "register"
                st.rerun()
        return

    if st.button("Back"):
        st.session_state.pop("student_auth_mode", None)
        st.rerun()

    if auth_mode == "login":
        st.title("Student Login", text_alignment="center")
        st.header("Log in using FaceID", text_alignment="center")
    else:
        st.title("Student Registration", text_alignment="center")
        st.header("Register using FaceID", text_alignment="center")

    photo_source = st.camera_input(
        "Position your face in the center",
        key=f"student_camera_{auth_mode}",
    )
    image_array = None

    if photo_source is not None:
        try:
            image_array = np.array(Image.open(photo_source).convert("RGB"))
        except Exception:
            st.error("Could not read the captured image. Please retake it.")

    if image_array is not None and auth_mode == "login":
        with st.spinner("AI is scanning..."):
            detected, _all_ids, num_faces = _recognise(photo_source.getvalue())

        if num_faces == 0:
            st.error("No face detected. Please try again.")
        elif num_faces > 1:
            st.error("Multiple faces detected. Please ensure only your face is visible.")
        elif detected:
            student_id = next(iter(detected))
            student = next(
                (s for s in get_all_students() if s["student_id"] == student_id),
                None,
            )
            if student is None:
                st.error(
                    "That face is recognised but has no student record. "
                    "Please contact an administrator."
                )
            else:
                st.session_state.is_logged_in = True
                st.session_state.user_id = "student"
                st.session_state.student_data = student
                _flash("Login successful!")
                st.rerun()
        else:
            st.error("Face not recognized. Please try again or choose Register.")

    if image_array is None or auth_mode != "register":
        return

    st.subheader("Complete your registration")
    new_name = st.text_input("Enter your Name")

    st.subheader("Optional: voice registration")
    st.info(
        "Voice registration is optional. You can skip this step if you "
        "prefer not to register your voice."
    )

    audio_data = None
    try:
        audio_data = st.audio_input("Record your voice (optional)")
    except Exception:
        st.warning(
            "Audio input is not supported in this environment. "
            "Please skip voice registration."
        )

    if st.button("Create Account", type="primary"):
        if not new_name or not new_name.strip():
            st.error("Please enter a valid name and try again.")
            return

        with st.spinner("Creating your account..."):
            encodings = src.screens.pipeline.face_pipeline.get_face_encodings(image_array)
            if not encodings:
                st.error(
                    "Couldn't extract a face encoding from that photo. "
                    "Please retake it and try again."
                )
                return

            voice_embedding = None
            if audio_data is not None:
                try:
                    voice_embedding = get_voice_embedding(audio_data.getvalue())
                except Exception:
                    st.warning(
                        "Voice could not be processed — "
                        "continuing with face-only registration."
                    )

            response_data = create_student(
                new_name.strip(),
                face_embedding=encodings[0].tolist(),
                voice_embedding=voice_embedding,
            )

            if not response_data:
                st.error("Registration failed. Please try again.")
                return

            src.screens.pipeline.face_pipeline.train_classifier()

            st.session_state.is_logged_in = True
            st.session_state.user_id = "student"
            st.session_state.student_data = response_data
            st.session_state.pop("student_auth_mode", None)
            _flash(f"Welcome, {new_name.strip()}!")
            st.rerun()


def subject_card(name, code, section, stats, footer_callback=None):
    with st.container(border=True):
        st.subheader(name)
        st.caption(f"{code} · Section {section}")
        stat_cols = st.columns(len(stats))
        for col, (icon, label, value) in zip(stat_cols, stats):
            col.metric(f"{icon} {label}", value)
        if footer_callback is not None:
            footer_callback()


def student_dashboard():
    dashboard_navigation()
    student_data = st.session_state.get("student_data", {})
    student_id = student_data['student_id']
    student_name = student_data.get("name", "Student")

    st.header("Student Dashboard", text_alignment="center")

    c1, c2 = st.columns([3, 1], vertical_alignment="center")
    with c1:
        st.subheader(f"Welcome, {student_name}")
    with c2:
        if st.button("Logout", type="secondary", key="loginbackbtn"):
            st.session_state["is_logged_in"] = False
            st.session_state.pop("student_data", None)
            st.session_state.pop("user_id", None)
            st.session_state.pop("student_auth_mode", None)
            st.rerun()

        st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.text('Your Enrolled Subjects', width='stretch')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects...'):
        subjects = get_students_subjects(student_id)
        logs = get_students_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    if not subjects:
        st.info("You are not enrolled in any subjects yet.")
        return

    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']

        stats = stats_map.get(sid, {"total":0, "attended": 0})

        def unenroll_btn(subject_id=sid):
            if st.button(
                "Unenroll from this course",
                type='tertiary',
                width='stretch',
                key=f"unenroll_{subject_id}",
            ):
                unenroll_student_to_subject(student_id, subject_id)
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_btn,
            )
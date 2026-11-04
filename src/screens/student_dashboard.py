import streamlit as st
from PIL import Image
import numpy as np
import io

from screens.pipeline.face_pipeline import (
    predict_attendance,
    get_face_encodings,
    train_classifier,
)
from screens.pipeline.voice_pipeline import get_voice_embedding
from screens.database.db import get_all_students, create_student


@st.cache_data(show_spinner=False, max_entries=16)
def _recognise(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return predict_attendance(np.array(image))


def _flash(msg: str, icon: str = "✅"):
    st.session_state["_flash"] = (msg, icon)


def _render_flash():
    flash = st.session_state.pop("_flash", None)
    if flash:
        st.toast(flash[0], icon=flash[1])

def student_dashboard():
    student_data = st.session_state.get("student_data", {})

    student_name = student_data.get("name", "Student")

    st.title("Student Dashboard", text_alignment="center")
    st.success(f"Welcome, {student_name}!")

    st.write("You are successfully logged in using FaceID.")

    if st.button("Logout", type="primary"):
        st.session_state.pop("student_data", None)
        st.session_state["is_logged_in"] = False
        st.session_state.pop("user_id", None)
        st.rerun()

        
def student_screen():
    if "student_data" in st.session_state:
        _render_flash()
        student_dashboard()
        return

    st.title("Student Dashboard", text_alignment="center")
    st.header("Login using FaceID", text_alignment="center")

    photo_source = st.camera_input("Position your face in the center")
    image_array = None

    if photo_source is not None:
        try:
            image_array = np.array(Image.open(photo_source).convert("RGB"))
        except Exception:
            st.error("Could not read the captured image. Please retake it.")

    show_registration = False

    if image_array is not None:
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
            st.info("Face not recognized. Might be a new student.")
            show_registration = True

    if not (show_registration and image_array is not None):
        return

    with st.expander("Register as a new student", expanded=True):
        st.header("New Student Registration", text_alignment="center")
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
                encodings = get_face_encodings(image_array)
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

                train_classifier()

                st.session_state.is_logged_in = True
                st.session_state.user_id = "student"
                st.session_state.student_data = response_data
                _flash(f"Welcome, {new_name.strip()}!")
                st.rerun()
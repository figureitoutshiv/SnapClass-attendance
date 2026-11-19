import streamlit as st
from PIL import Image
from src.screens.database.db import create_subject

@st.dialog("Capture or Upload Photo", width="stretch")

def add_photos_dialog():
    st.write('Add classroom photos to scan for attendance.')

    if 'photos_tab' not in st.session_state:
        st.session_state.photos_tab = 'camera'

    t1, t2 = st.columns(2)

    with t1:
        type_camera = "primary" if st.session_state.photos_tab == 'camera' else "secondary"
        if st.button("Camera", type=type_camera, width="stretch"):
            st.session_state.photos_tab = 'camera'
            st.rerun()

    with t2:
        type_upload = "primary" if st.session_state.photos_tab == 'upload' else "secondary"
        if st.button("Upload", type=type_upload, width="stretch"):
            st.session_state.photos_tab = 'upload'
            st.rerun()

    if st.session_state.photos_tab == 'camera':
        cam_photo = st.camera_input("Take a photo")
        if cam_photo:
            st.session_state.attendance_image.append(Image.open(cam_photo))
            st.toast("Photo added successfully!")
            st.rerun()

    if st.session_state.photos_tab == 'upload':
        uploaded_files = st.file_uploader('Choose image files', type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key="dialog_upload")
        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_image.append(Image.open(f))

            st.toast(f"{len(uploaded_files)} photo(s) added successfully!")
            st.rerun()

        st.divider()
        if st.button('Done', type='primary', width="stretch"):
            st.session_state.photos_tab = 'camera'
            st.rerun()


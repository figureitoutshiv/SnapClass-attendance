import streamlit as st
import time

from src.screens.components.dialog_create_subject import create_subject_dialog
from src.screens.components.dialog_share_subject import share_subject_dialog
from src.screens.components.subject_card import subject_card

from src.screens.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects
)
from src.screens.components.navigation import dashboard_navigation
from src.screens.ui.base_layout import (
    load_fonts,
    style_base_layout,
    style_background_dashboard,
)


def teacher_dashboard():
    load_fonts()
    style_base_layout()
    style_background_dashboard()
    dashboard_navigation()

    st.session_state.setdefault("teacher_login_type", "login")

    if st.session_state.get("teacher_data"):
        teacher_logged_in_view()
        return

    st.title("Teacher Dashboard")

    if st.session_state["teacher_login_type"] == "login":
        teacher_screen_login()
    else:
        teacher_screen_register()


def teacher_logged_in_view():
    teacher_data = st.session_state["teacher_data"]

    head1, head2 = st.columns([4, 1])

    with head1:
        st.header(f"Welcome, {teacher_data['name']}")

    with head2:
        if st.button(
            "Logout",
            icon=":material/logout:",
            key="teacher_logout"
        ):
            st.session_state.pop("teacher_data", None)
            st.session_state.pop("current_teacher_tab", None)
            st.rerun()

    st.session_state.setdefault("current_teacher_tab", "take_attendance")

    st.divider()
    tabs = [
        ("take_attendance", "Take Attendance", ":material/ar_on_you:"),
        ("manage_subjects", "Manage Subjects", ":material/book_ribbon:"),
        ("attendance_records", "Attendance Records", ":material/cards_stack:"),
    ]

    # Navigation buttons
    cols = st.columns(len(tabs))

    for col, (key, label, icon) in zip(cols, tabs):
        with col:
            btn_type = (
                "primary"
                if st.session_state.current_teacher_tab == key
                else "primary"
            )

            if st.button(
                label,
                icon=icon,
                type=btn_type,
                width="stretch",
                key=f"tab_{key}"
            ):
                st.session_state.current_teacher_tab = key
                st.rerun()

    # Divider below navigation buttons
    st.divider()

    # Display selected tab content BELOW navigation
    current = st.session_state.current_teacher_tab

    if current == "take_attendance":
        teacher_tab_take_attendance()

    elif current == "manage_subjects":
        teacher_tab_manage_subjects()

    elif current == "attendance_records":
        teacher_tab_attendance_records()


def teacher_tab_take_attendance():
    st.write("Attendance tab Selected.")

def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]

    col1, col2 = st.columns([4, 3])

    with col1:
        st.write("Subjects tab Selected.")

    with col2:
        if st.button(
            "Create New Subject",
            width="stretch",
            key="create_new_subject"
        ):
            create_subject_dialog(teacher_id)

    #LIST all subjects
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👥", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes'])
            ]

            def share_btn():
                if st.button(
                    f"Share Code: {sub['name']}",
                    key=f"share_{sub['subject_code']}",
                    icon=":material/share:"
                ):
                    share_subject_dialog(sub['name'], sub['subject_code'])
                st.space()

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn
            )
    else:
        st.info("No Subjects found. Create a new subject to get started.")


def teacher_tab_attendance_records():
     st.write("Records tab Selected.")


def teacher_screen_login():
    teacher_username = st.text_input(
        "Username", placeholder="Enter your username", key="login_username"
    )
    teacher_password = st.text_input(
        "Password", placeholder="Enter your password",
        type="password", key="login_password",
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button("Login", icon=":material/passkey:", type="primary",
                     key="teacher_login", width="stretch"):
            if not teacher_username or not teacher_password:
                st.warning("Please enter your username and password.")
            else:
                teacher_data = teacher_login(teacher_username, teacher_password)
                if teacher_data:
                    teacher_data.pop("password", None)
                    st.session_state["teacher_data"] = teacher_data
                    st.toast("Welcome back!", icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with btnc2:
        if st.button("Register Instead", icon=":material/person_add:",
                     type="primary", key="teacher_register_switch",
                     width="stretch"):
            st.session_state["teacher_login_type"] = "register"
            st.rerun()


def register_teacher(username, name, email, password, confirm):
    if not username or not name or not password:
        return False, "Username, full name, and password are required."

    if password != confirm:
        return False, "Passwords do not match."

    if check_teacher_exists(username):
        return False, "Username already taken. Try a different one."

    try:
        # Make sure create_teacher(username, password, name, email) accepts email
        create_teacher(username, password, name, email)
        return True, "Successfully created! Login now."
    except Exception:
        return False, "Registration failed. Please try again."


def teacher_screen_register():
    teacher_username = st.text_input(
        "Username",
        placeholder="Enter your username",
        key="register_username",
    )

    teacher_name = st.text_input(
        "Full Name",
        placeholder="Enter your full name",
        key="register_name",
    )

    teacher_email = st.text_input(
        "Email", placeholder="Enter your email address", key="register_email"
    )

    teacher_password = st.text_input(
        "Password", placeholder="Create a password",
        type="password", key="register_password",
    )

    teacher_confirm_password = st.text_input(
        "Confirm Password", placeholder="Re-enter your password",
        type="password", key="register_confirm_password",
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button("Login Instead", icon=":material/login:", type="primary",
                     key="register_login_button", width="stretch"):
            st.session_state["teacher_login_type"] = "login"
            st.rerun()

    with btnc2:
        if st.button("Register", icon=":material/person_add:", type="primary",
                     key="teacher_register_submit", width="stretch"):
            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_email,
                teacher_password,
                teacher_confirm_password,
            )

            if success:
                st.toast(message, icon="✅")
                time.sleep(1)
                st.session_state["teacher_login_type"] = "login"
                st.rerun()
            else:
                st.error(message)
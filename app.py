import sys
from pathlib import Path

from src.screens.components.auto_enroll_dialog import auto_enroll_dialog


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.screens.home_dashboard import home_dashboard
from src.screens.student_dashboard import student_screen
from src.screens.teacher_dashboard import teacher_dashboard
from src.screens.ui.base_layout import style_base_layout

def main():
    style_base_layout()

    if 'login_type' not in st.session_state:
        st.session_state["login_type"] = None

    match st.session_state["login_type"]:
        case 'teacher':
            teacher_dashboard()
        case 'student':
            student_screen()
        case None:
            home_dashboard()

    join_code = st.query_params.get('join-code')
    if join_code:
        if st.session_state.login_type != 'student':
            st.session_state.login_type = 'student'
            st.rerun()

        if st.session_state.get('student_data'):
            auto_enroll_dialog(join_code)

main()
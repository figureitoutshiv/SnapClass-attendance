import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.screens.home_dashboard import home_dashboard
from src.screens.student_dashboard import student_dashboard
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
            student_dashboard()
        case None:
            home_dashboard()

if __name__ == "__main__":
    main()
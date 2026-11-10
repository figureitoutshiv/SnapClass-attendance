import os

import streamlit as st
from supabase import create_client, Client


def _get_setting(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        value = st.secrets.get(name)
    if not value:
        raise RuntimeError(f"Configure {name} in Streamlit secrets or the environment.")
    return value


SUPABASE_URL = _get_setting("SUPABASE_URL")
SUPABASE_KEY = _get_setting("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
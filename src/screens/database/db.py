import os

import streamlit as st
from supabase import Client, create_client

from src.screens.database.config import SUPABASE_KEY, SUPABASE_URL, supabase


def get_admin_supabase() -> Client:
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_role_key:
        service_role_key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY")
    if not service_role_key:
        raise RuntimeError(
            "Subject creation requires SUPABASE_SERVICE_ROLE_KEY. "
            "Configure it in Streamlit secrets or the server environment."
        )
    if service_role_key == SUPABASE_KEY or service_role_key.startswith(
        "sb_publishable_"
    ):
        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY contains a publishable/anon key. "
            "Set it to the server-side secret/service_role key from Supabase."
        )

    return create_client(SUPABASE_URL, service_role_key)


def check_teacher_exists(username):
    response = (
        supabase.table("teachers")
        .select("username")
        .eq("username", username)
        .execute()
    )
    return len(response.data) > 0


def create_teacher(username, password, name):
    response = supabase.table("teachers").insert({
        "username": username,
        "password": password,
        "name": name,
    }).execute()
    return response


def teacher_login(username, password):
    response = (
        supabase.table("teachers")
        .select("*")
        .eq("username", username)
        .eq("password", password)
        .execute()
    )
    if response.data:
        return response.data[0]
    return None


def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_student(name, face_embedding=None, voice_embedding=None):
    data = {
        "name": name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding,
    }
    response = supabase.table("students").insert(data).execute()
    return response.data[0] if response.data else None

def create_subject(teacher_id, subject_code, name, section):
    data = {
        "teacher_in": teacher_id,
        "subject_code": subject_code,
        "name": name,
        "section": section,
    }
    response = get_admin_supabase().table("subjects").insert(data).execute()
    return response.data

def get_teacher_subjects(teacher_id):
    teacher_data = st.session_state.get("teacher_data")
    if not teacher_data or teacher_data.get("teacher_id") != teacher_id:
        raise PermissionError("You must be logged in as this teacher to view subjects.")

    response = (
        get_admin_supabase()
        .table("subjects")
        .select("*, subject_student(count), attendance_logs(timestamp)")
        .eq("teacher_in", teacher_id)
        .execute()
    )
    subjects = response.data

    for sub in subjects:
        sub['total_students'] = sub.get("subject_student", [{}])[0].get("count", 0) if sub.get("subject_student") else 0
        attendance = sub.get("attendance_logs", [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions
        sub.pop('subject_student', None)
        sub.pop('attendance_logs', None)

    return subjects

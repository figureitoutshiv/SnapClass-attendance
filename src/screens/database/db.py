from src.screens.database.config import supabase


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
    response = supabase.table("student").select("*").execute()
    return response.data

def create_student(name, face_embedding=None, voice_embedding=None):
    data = {
        "name": name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding,
    }
    response = supabase.table("student").insert(data).execute()
    return response.data[0] if response.data else None
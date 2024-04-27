import os
from dotenv import load_dotenv


load_dotenv()


class Endpoints:
    ME = "/users/me"
    LOGIN = "/auth/login"
    REFRESH = "/auth/refresh"
    LOGOUT = "/auth/logout"


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "")
    assert SECRET_KEY, "No SECRET_KEY set for application"
    SESSION_KEY = "supabase.auth.token"
    ACCESS_TOKEN_KEY = "myapp.access_token"
    REFRESH_TOKEN_KEY = "myapp.refresh_token"
    BACKEND_BASE_URL = "http://127.0.0.1:8000"

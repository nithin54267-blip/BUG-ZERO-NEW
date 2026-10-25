import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    DATABASE_PATH = os.path.join(BASE_DIR, os.getenv("DATABASE_PATH", "database/bugzero.db"))
    SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
    FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
    JWT_HOURS = 24
    MAX_CODE_CHARS = 20000
    MAX_PROBLEM_CHARS = 5000

import sqlite3
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from middleware.auth_middleware import create_token
from models import db
from utils.helpers import valid_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if len(username) < 3:
        return jsonify(error="Username must be at least 3 characters."), 400
    if not valid_email(email):
        return jsonify(error="Enter a valid email address."), 400
    if len(password) < 8:
        return jsonify(error="Password must be at least 8 characters."), 400
    if db.user_exists(username, email):
        return jsonify(error="That username or email is already registered."), 409

    try:
        user_id = db.create_user(username, email, generate_password_hash(password))
    except sqlite3.IntegrityError:
        return jsonify(error="That username or email is already registered."), 409
    return jsonify(token=create_token(user_id, username), username=username), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = db.find_user((data.get("identifier") or "").strip())
    if not user or not check_password_hash(user["password_hash"], data.get("password") or ""):
        return jsonify(error="Wrong email/username or password."), 401
    return jsonify(token=create_token(user["id"], user["username"]), username=user["username"])

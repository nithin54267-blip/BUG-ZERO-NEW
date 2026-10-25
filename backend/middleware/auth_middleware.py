from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import g, jsonify, request
from config import Config


def create_token(user_id, username):
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=Config.JWT_HOURS),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="Please log in to continue."), 401
        try:
            data = jwt.decode(header[7:], Config.SECRET_KEY, algorithms=["HS256"])
            g.user_id = int(data["sub"])
            g.username = data["username"]
        except jwt.ExpiredSignatureError:
            return jsonify(error="Your session expired. Please log in again."), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid session. Please log in again."), 401
        return fn(*args, **kwargs)
    return wrapper

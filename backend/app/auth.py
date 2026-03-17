from __future__ import annotations

from functools import wraps
from typing import Optional

from flask import current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from .models import User


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def _serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config["SECRET_KEY"]
    return URLSafeTimedSerializer(secret_key=secret_key, salt="skill-gap-auth")


def create_auth_token(user_id: int) -> str:
    return _serializer().dumps({"user_id": user_id})


def verify_auth_token(token: str, max_age_seconds: int = 60 * 60 * 24 * 7) -> Optional[int]:
    try:
        payload = _serializer().loads(token, max_age=max_age_seconds)
        return int(payload.get("user_id"))
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None


def get_user_from_request() -> Optional[User]:
    header = request.headers.get("Authorization", "")
    token = ""
    if header.startswith("Bearer "):
        token = header.split(" ", 1)[1].strip()
    elif request.args.get("token"):
        token = str(request.args.get("token", "")).strip()

    if not token:
        return None

    user_id = verify_auth_token(token)
    if not user_id:
        return None

    return User.query.get(user_id)


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_user_from_request()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)

    return wrapper

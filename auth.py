import os
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, HTTPException, status

SECRET_KEY = os.environ.get("SECRET_KEY", "cambiar-esta-clave-en-produccion")
serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_session_token(username: str) -> str:
    return serializer.dumps({"username": username})


def get_current_admin(request: Request) -> str:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})
    try:
        data = serializer.loads(token, max_age=60 * 60 * 8)  # 8 horas
        return data["username"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})

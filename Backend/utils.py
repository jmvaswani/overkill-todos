from cryptography.fernet import Fernet
import jwt
from datetime import datetime, timedelta
from __main__ import app
from password_strength import PasswordPolicy

policy = PasswordPolicy.from_names(length=8, uppercase=1, numbers=1, special=1)

fernkey = app.config["FERNET"]
f = Fernet(fernkey)

allowed_types = {
    "id": str,
    "username": str,
    "password": str,
    "expiry": str,
    "title": str,
    "description": str,
    "todo": dict,
}


def check_types(data: dict):
    for key in data:
        if key not in allowed_types:
            return False
        if type(data[key]) != allowed_types[key]:
            return False
    return True


def encrypt_password(password):
    global f
    return f.encrypt(password.encode()).decode()


def decrypt_password(password):
    global f
    return f.decrypt(password.encode()).decode()


def generate_token(id, username):
    jwtToken = jwt.encode(
        {
            "id": id,
            "username": username,
            "exp": datetime.utcnow() + timedelta(days=5),
        },
        app.config["SECRET_KEY"],
    )
    return jwtToken


{"username": str, "password": str, "token": str, "todos": []}


def check_password(password):
    global policy
    return policy.test(password)

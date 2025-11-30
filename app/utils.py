import jwt
from datetime import datetime, timedelta, UTC
from werkzeug.utils import escape
from app.config import JWT_SECRET_KEY

def generate_token(username):
    """Генерация JWT токена для пользователя"""
    payload = {
        'username': username,
        'exp': datetime.now(UTC) + timedelta(hours=24),
        'iat': datetime.now(UTC)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

def sanitize_input(data):
    """Санитизация пользовательских данных для защиты от XSS"""
    if isinstance(data, str):
        return escape(data)
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


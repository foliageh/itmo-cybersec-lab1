from functools import wraps
from flask import request, jsonify
import jwt
from app.config import JWT_SECRET_KEY

def token_required(f):
    """Middleware для проверки JWT токена"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Проверка заголовка Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Формат: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Декодирование токена
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            # Добавляем информацию о пользователе в request
            request.current_user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


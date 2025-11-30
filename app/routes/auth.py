from flask import Blueprint, request, jsonify
import bcrypt
from app.database import get_db
from app.utils import generate_token, sanitize_input

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Санитизация входных данных
        username = sanitize_input(data['username'])
        password = data['password']
        
        if not username or not password:
            return jsonify({'error': 'Username and password cannot be empty'}), 400
        
        # Проверка минимальной длины пароля
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Проверка существования пользователя (параметризованный запрос)
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Хэширование пароля с помощью bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Создание пользователя (параметризованный запрос)
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'User registered successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Аутентификация пользователя"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Санитизация входных данных
        username = sanitize_input(data['username'])
        password = data['password']
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Поиск пользователя (параметризованный запрос)
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Проверка пароля
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Генерация JWT токена
            token = generate_token(user['username'])
            return jsonify({
                'token': token,
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500


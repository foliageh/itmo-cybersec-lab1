from flask import Blueprint, jsonify
from app.database import get_db
from app.middleware import token_required
from app.utils import sanitize_input

api_bp = Blueprint('api', __name__)

@api_bp.route('/data', methods=['GET'])
@token_required
def get_data():
    """Получение списка пользователей (только для аутентифицированных пользователей)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Получение списка пользователей
        cursor.execute('SELECT id, username, created_at FROM users')
        users = cursor.fetchall()
        conn.close()
        
        # Преобразование результатов в список словарей
        users_list = []
        for user in users:
            user_dict = {
                'id': user['id'],
                'username': user['username'],
                'created_at': user['created_at']
            }
            # Санитизация данных перед отправкой (защита от XSS)
            user_dict = sanitize_input(user_dict)
            users_list.append(user_dict)
        
        return jsonify({
            'users': users_list,
            'count': len(users_list)
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve data'}), 500


import os

# Путь к базе данных
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

# Секретные ключи (в продакшене должны быть в переменных окружения)
SECRET_KEY = os.environ.get('SECRET_KEY', 'secret-key-change-in-production')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')


from flask import Flask
from app.database import init_db
from app.config import SECRET_KEY, JWT_SECRET_KEY

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    
    # Инициализация базы данных
    init_db()
    
    # Регистрация blueprints
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app


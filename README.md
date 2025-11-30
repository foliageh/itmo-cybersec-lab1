# Информационная безопасность - Лабораторная №1

Проект представляет собой защищенное REST API приложение на Flask с интеграцией инструментов безопасности в CI/CD pipeline. Реализованы меры защиты от основных уязвимостей из OWASP Top 10.

## Технологический стек

- **Python 3.12+**
- **Flask** - веб-фреймворк
- **SQLite** - база данных
- **PyJWT** - работа с JWT токенами
- **bcrypt** - хэширование паролей
- **Werkzeug** - утилиты безопасности (экранирование)

## Установка и запуск

### Предварительные требования

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - менеджер пакетов

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd itmo-cybersec-lab1
```

2. Установите зависимости:
```bash
uv sync
```

3. Запустите приложение:
```bash
uv run python main.py
```

Приложение будет доступно по адресу `http://localhost:5000/`.

## Описание API

### 1. POST /auth/register

Регистрация нового пользователя.

**Запрос:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**Ответ (успех):**
```json
{
  "message": "User registered successfully"
}
```
Статус: 201

**Ответ (ошибка):**
```json
{
  "error": "Username already exists"
}
```
Статус: 409

### 2. POST /auth/login

Аутентификация пользователя.

**Запрос:**
```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**Ответ (успех):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "Login successful"
}
```
Статус: 200

**Ответ (ошибка):**
```json
{
  "error": "Invalid credentials"
}
```
Статус: 401

### 3. GET /api/data

Получение списка пользователей. **Требует аутентификации.**

**Заголовки:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Ответ (успех):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "testuser",
      "created_at": "2025-01-01 12:00:00"
    }
  ],
  "count": 1
}
```
Статус: 200

**Ответ (ошибка):**
```json
{
  "error": "Token is missing"
}
```
Статус: 401

## Тестирование

**Примеры CURL-запросов:**

1. Регистрация пользователя:
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

2. Логин:
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

3. Получение данных (с токеном):
```bash
curl -X GET http://localhost:5000/api/data \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Реализованные меры защиты

### 1. Защита от SQL-инъекций (SQLi)

Во всех местах работы с базой данных используются **параметризованные запросы** (prepared statements). Это гарантирует, что пользовательский ввод обрабатывается как данные, а не как исполняемый код.

**Пример реализации:**
```python
cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
```

### 2. Защита от XSS (Cross-Site Scripting)

Все пользовательские данные, возвращаемые в ответах API, проходят через функцию `sanitize_input()`, которая использует `werkzeug.utils.escape()` для экранирования специальных символов.

**Пример реализации:**
```python
from werkzeug.utils import escape

def sanitize_input(data):
    if isinstance(data, str):
        return escape(data)
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data
```

### 3. Защита от Broken Authentication

#### 3.1. Хэширование паролей

Пароли хэшируются с помощью **bcrypt** - современного алгоритма хэширования с солью. Bcrypt автоматически генерирует уникальную соль для каждого пароля и использует адаптивную функцию, что делает перебор паролей вычислительно дорогим.

**Пример реализации:**
```python
# Хэширование пароля при регистрации
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Проверка пароля при логине
if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
    # Пароль верный
```

#### 3.2. JWT-токены для аутентификации

После успешного логина пользователю выдается **JWT-токен**, который содержит информацию о пользователе и срок действия (24 часа). Все защищенные эндпоинты требуют валидный JWT токен в заголовке `Authorization`.

**Пример реализации:**
```python
def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.now(UTC) + timedelta(hours=24),
        'iat': datetime.now(UTC)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token
```

#### 3.3. Middleware для проверки токенов

Реализован декоратор `@token_required`, который автоматически проверяет наличие и валидность JWT токена перед выполнением функции эндпоинта.

**Пример реализации:**
```python
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            request.current_user = data['username']
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated
```

## Отчеты SAST/SCA

После выполнения pipeline отчеты доступны в разделе "Actions" репозитория:
- **Bandit Report** (JSON) - показывает отсутствие критических уязвимостей в коде
- **Safety Report** (JSON) - показывает отсутствие уязвимостей в зависимостях
- **OWASP Dependency-Check Report** (HTML) - детальный анализ всех зависимостей

.... скрины ....

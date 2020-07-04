# Импоритируем библиотеки

# Основные файлы
from flask import Flask
from flask_login import LoginManager


def get_app_and_login_manager():
    """Функция возвращает объект приложения и авторизации"""

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gjlk;fdgnfedbf80094223r9fomzc,vl0eruhrwlkv'

    login_manager = LoginManager()
    login_manager.init_app(app)

    return app, login_manager

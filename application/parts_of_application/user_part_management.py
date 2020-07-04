"""Этот файл предназначен для создания функций, связанных с пользователем"""

# Импортируем необходимые файлы

# Загружаем формы для авторизации, регистрации и изменения профиля
from data.forms.login_form import LoginForm
from data.forms.register_form import RegisterForm
from data.forms.edit_profile_form import EditProfileForm

# Загружаем класс таблицы пользователей
from data.tables.user import User

# Специальные функции
from flask import render_template, request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from random import randint
from os import remove

# Часть для работы с БД
from data.database.all_for_session import create_session


def init(login_manager, app):

    @login_manager.user_loader
    def load_user(user):
        """Просто загрузка пользователя"""

        db_session = create_session()
        return db_session.query(User).get(user)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Обработчик для авторизации"""

        form = LoginForm()

        if form.validate_on_submit():

            # Загружаем пользователя
            db_session = create_session()
            user = db_session.query(User).filter(User.email == form.email.data).first()

            # Проверяем пароль
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect('/')

            # В противном случае возвращяем сообщение об ошибке
            return render_template("login.html", message="Неправильный логин или пароль", form=form, title='Вход')

        return render_template("login.html", form=form, title='Вход')

    @app.route('/logout')
    @login_required
    def logout():
        """Выход из аккаунта"""

        logout_user()
        return redirect("/")

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Обработчик для регистрации"""

        form = RegisterForm()

        if form.validate_on_submit():

            # Создаём пользователя
            db_session = create_session()
            user = User()

            user.name = form['name'].data
            user.surname = form['surname'].data
            user.fatherhood = form['fatherhood'].data
            user.grade = form['grade'].data
            user.email = form['email'].data
            user.set_password(form['password'].data)

            # Проверка на наличие пользователя с таким же адресом почты
            if db_session.query(User).filter(User.email == user.email).first():
                return render_template("register.html", form=form, message_email="Этот логин уже занят")

            db_session.add(user)
            db_session.commit()

            # Загружаем только что созданного пользователя для загрузки фото
            user = db_session.query(User).filter(User.email == user.email).first()

            # Загрузка фото
            data = form['photo'].data.read()

            if data:
                user.photo = f'../static/img/avatars/{user.id}-v1.jpg'
                with open(f'static/img/avatars/{user.id}-v1.jpg', 'wb') as file:
                    file.write(data)
            else:
                user.photo = f'../static/img/avatars/default.jpg'

            login_user(user)
            db_session.commit()

            return redirect("/")
        else:
            return render_template("register.html", form=form, title='Регистрация')

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        """Обработчик страницы для изменения пользователя"""

        form = EditProfileForm()

        if form.validate_on_submit():

            # Изменяем текущего пользователя
            db_session = create_session()
            current_user.name = form['name'].data
            current_user.surname = form['surname'].data
            current_user.fatherhood = form['fatherhood'].data
            current_user.grade = form['grade'].data
            current_user.set_password(form['password'].data)

            # Удаляем старую фотографию
            if current_user.photo != '../static/img/avatars/default.jpg':
                try:
                    remove(current_user.photo.lstrip('../'))
                except FileNotFoundError:
                    pass

            # Загружаем фотку
            data = form['photo'].data.read()
            if data:
                number = randint(0, 2 ** 64)  # Для изменения фотки (чтобы она не кэшировалась)
                current_user.photo = f'../static/img/avatars/{current_user.id}-{number}.jpg'
                with open(f'static/img/avatars/{current_user.id}-{number}.jpg', 'wb') as file:
                    file.write(data)
            else:
                current_user.photo = '../static/img/avatars/default.jpg'

            db_session.merge(current_user)
            db_session.commit()

            return redirect("/")

        if request.method == "GET":
            # Задаём параметры формы
            form.name.data = current_user.name
            form.surname.data = current_user.surname
            form.fatherhood.data = current_user.fatherhood
            form.grade.data = current_user.grade
            form.email.data = current_user.email

        return render_template("edit_profile.html", form=form, title='Изменение профиля')

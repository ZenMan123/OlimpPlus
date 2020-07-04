"""Этот файл предназначен для создания функций, связанных с добавлением информации"""

# Импортируем необходимые файлы

# Загружаем формы для заданий
from data.forms.add_news_form import AddNewsForm
from data.forms.add_olimpiads_group_form import AddOlimpiadsGroupForm

# Загружаем классы таблиц
from data.tables.olimpiad_registration import OlimpiadRegistration
from data.tables.olimpiads_group import OlimpiadsGroup
from data.tables.olimpiads_group_news import OlimpiadsGroupNews
from data.tables.olimpiad import Olimpiad
from data.tables.user import User

# Для Flask
from flask import render_template, redirect
from flask_login import login_required, current_user

# Для задания путей до фотки
from random import randint

# Часть для работы с БД
from data.database.all_for_session import create_session

# Используется для добавления файлов (не поддерживается кириллица)
from useful_things import RUS_TO_ENG

import datetime


def init(app):

    def add_registration(olimpiads_group):
        """Добавляет дату регистрации для группы олимпиад.
        Пока все даты заполняются на один день, потому что
        нет реальных данных, а это просто тестовые данные. Если раскомментировать код,
        то можно будет добавлять даты и документы для каждой олимпиады через интерфейс командной строки."""

        for olimpiad in olimpiads_group.olimpiads:
            # Указываем дату и необходимые документы
            registr = OlimpiadRegistration()
            registr.date = datetime.datetime(year=2020, month=8, day=25)
            registr.documents = "Тут будут необходимые документы"  # Пока эта функция не реализована
            olimpiad.registration_data = registr

    def add_tasks(olimpiads_group):
        """Добавляем задания для олимпиад. Пока они все пустые, но их нужно просто заполнить"""

        # Предметы и классы
        subjects = olimpiads_group.subjects.split(', ')
        grades = olimpiads_group.grades.split(', ')

        # Создаём необходимые файлы для загрузки заданий
        for subject in subjects:
            for grade in grades:
                # Создаем zip архив
                with open(f'static/tasks/{olimpiads_group.id}_{RUS_TO_ENG[subject]}_{grade}.zip', 'w') as file:
                    pass

    @app.route('/add_news', methods=["GET", "POST"])
    @login_required
    def add_news():
        """Страничка для добавления админом новостей. Пока админ - пользователь с id = 1,
        но это легко исправляется."""

        if not is_admin(current_user):
            return redirect('/')

        form = AddNewsForm()

        if form.validate_on_submit():

            # Создаём новость
            db_session = create_session()
            news_to_add = make_news_by_form(form)

            # Если новость связана с группой олимпиад, то добавляем искомую новость в группу олимпиад
            # Новость может быть не только об олимпиадах. Например, обновление работы сайта
            if form['is_group_news'].data:
                olimpiads_group = get_olimpiads_group_by_name(form['group_name'].data)
                if not olimpiads_group:  # Если нет такой олимпиады
                    return render_template("add_news.html", form=form, message="Группа олимпиад не найдена")
                olimpiads_group.news.append(news_to_add)

                db_session.merge(olimpiads_group)

            else:
                db_session.add(news_to_add)
                db_session.commit()

            # Получаем новость (нам нужен её id) и загружаем фотку
            news_to_add = db_session.query(OlimpiadsGroupNews).all()[-1]
            set_path_to_image(news_to_add, form['photo'].data.read(), 'news')

            db_session.commit()

            # Возвращаемся на главную страницу
            return redirect('/')

        return render_template("add_news.html", form=form, title='Добавление новости')

    @app.route('/add_olimp_group', methods=["GET", "POST"])
    @login_required
    def add_olimp_group():
        """Страницка для добавления админом групп олимпиад"""

        if not is_admin(current_user):
            return redirect('/')

        form = AddOlimpiadsGroupForm()
        if form.validate_on_submit():
            # Создаём группу олимпиад
            olimpiads_group = make_olimpiads_group_by_form(form)

            # Нужно получить id олимпиады в БД, поэтому её надо загрузить и выгрузить от туда
            db_session = create_session()
            db_session.add(olimpiads_group)
            db_session.commit()

            db_session = create_session()
            olimpiads_group = db_session.query(OlimpiadsGroup).all()[-1]  # Получаем строку из БД

            set_path_to_image(olimpiads_group, form['photo'].data.read(), 'olimpiads')  # Загружаем фотографию
            add_registration(olimpiads_group)  # Добавляем даты регистрации и все такое
            add_tasks(olimpiads_group)  # Добавляем файлы заданий

            db_session.commit()

            # Возвращаемся на главную страницу
            return redirect('/olimpiads')

        return render_template("add_olimpiads_group.html", form=form, title='Добавление олимпиад')

    @app.route('/add_admin/<int:user_id>')
    @login_required
    def add_admin(user_id):
        """Делает пользователя админом"""

        if is_admin(current_user):
            db_session = create_session()
            user = db_session.query(User).get(user_id)
            if user:
                user.is_admin = True
            db_session.commit()

        return redirect('/')

    @app.route('/del_olimp/<int:olimpiads_group_id>')
    @login_required
    def del_olimpiads_group(olimpiads_group_id):
        """Удаляет группу олимпиад"""

        if not is_admin(current_user):
            return redirect('/')

        db_session = create_session()
        olimpiads_group = db_session.query(OlimpiadsGroup).get(olimpiads_group_id)
        if olimpiads_group:
            db_session.delete(olimpiads_group)
            db_session.commit()

        return redirect('/olimpiads')

    @app.route('/del_news/<int:news_id>')
    @login_required
    def del_news(news_id):
        """Удаляет новость"""

        if not is_admin(current_user):
            return redirect('/')

        db_session = create_session()
        news = db_session.query(OlimpiadsGroupNews).get(news_id)
        if news:
            db_session.delete(news)
            db_session.commit()

        return redirect('/')


def is_admin(user):
    """Возвращает True, если пользователь админ и False в противном случае"""
    return user.id == 1 or user.is_admin


def get_olimpiads_group_by_name(name):
    db_session = create_session()
    return db_session.query(OlimpiadsGroup).filter(
        OlimpiadsGroup.name == name).first()


def set_path_to_image(obj, data, obj_type):
    """Загружает картинку и указывает пути до неё
    obj_type - тип объекта (например, news или olimpiads)"""

    number = randint(1, 2 ** 64)
    if data:
        obj.photo = f'../static/img/{obj_type}/{obj.id}-{number}.jpg'
        with open(f'static/img/{obj_type}/{obj.id}-{number}.jpg', 'wb') as file:
            file.write(data)
    else:
        obj.photo = f'../static/img/{obj_type}/default.jpg'


def make_news_by_form(form):
    return OlimpiadsGroupNews(title=form['title'].data,
                              description=form['description'].data,
                              text=form['text'].data.replace('\r', '\n'))


def make_olimpiads_group_by_form(form):
    olimpiads_group = OlimpiadsGroup(name=form['name'].data,
                                     organizer=form['organizer'].data,
                                     description=form['description'].data.replace('\r', '\n'),
                                     subjects=', '.join(form['subjects'].data),
                                     grades=', '.join(form['grades'].data),
                                     grades_description=f"{form['grades'].data[0]} - {form['grades'].data[-1]} классы",
                                     cities=', '.join(form['cities'].data + form['extra_cities'].data.split(', ')),
                                     link=form['link'].data)

    # Добавляем олимпиады конкретного класса, города и предмета
    for grade in olimpiads_group.grades.split(', '):
        for subject in olimpiads_group.subjects.split(', '):
            olimpiads_group.olimpiads.append(Olimpiad(grade=grade, subject=subject))

    return olimpiads_group

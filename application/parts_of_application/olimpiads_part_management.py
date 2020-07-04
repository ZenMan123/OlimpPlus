"""Этот файл предназначен для создания функций, связанных с олимпиадами (их отображением)"""

# Импортируем необходимые файлы

# Загружаем функции для загрузки формы для заданий
import data.forms.task_form
import data.forms.register_olimp_form

# Загружаем классы таблиц
from data.tables.user import User
from data.tables.olimpiads_group import OlimpiadsGroup
from data.tables.olimpiads_group_news import OlimpiadsGroupNews
from data.tables.olimpiad import Olimpiad

# Flask
from flask import render_template, redirect, abort
from flask_login import login_required, current_user

# Часть для работы с БД
from data.database.all_for_session import create_session

# Расписание
from useful_things import TimeTable


def init(app):

    @app.route('/why_olimps')
    def why_olimps():
        """Страница о том, зачем писать олимпиады"""

        return render_template("why_olimps.html", title='Зачем писать олимпиады')

    @app.route('/olimpiads')
    def olimpiads():
        """Страница, отображающая все олимпиады"""

        # Выбираем все олимпиады
        db_session = create_session()
        all_olimpiads = db_session.query(OlimpiadsGroup).all()
        db_session.close()

        # Делаем по три олимпиады в ряду
        olimpiads_in_rows = []
        for i in range(0, len(all_olimpiads), 3):
            olimpiads_in_rows.append(all_olimpiads[i: min(len(all_olimpiads), i + 3)])

        return render_template("olimpiads.html", olimpiads=olimpiads_in_rows, title='Олимпиады')

    @app.route('/user_olimpiads')
    @login_required
    def user_olimpiads():
        """Отображение олимпиад пользователя"""

        db_session = create_session()
        user = db_session.query(User).filter(User.email == current_user.email).first()
        all_olimpiads = user.olimpiads

        # По три олимпиады в ряду
        olimpiads_in_rows = []
        for i in range(0, len(all_olimpiads), 3):
            olimpiads_in_rows.append(all_olimpiads[i: min(len(all_olimpiads), i + 3)])

        return render_template("user_olimpiads.html", olimpiads=olimpiads_in_rows)

    @app.route('/particular_olimpiad/<int:olimpiads_group_id>')
    def particular_olimpiad(olimpiads_group_id):
        """Страница для конкретной олимпиады"""

        # Получаем группу олимпиад
        db_session = create_session()
        item = db_session.query(OlimpiadsGroup).filter(OlimpiadsGroup.id == olimpiads_group_id).first()

        if not item:
            abort(404)

        # Получаем список предметов
        subjects = item.subjects.split(', ')

        # Получаем все новости
        all_news = sorted(db_session.query(OlimpiadsGroupNews).filter(
            OlimpiadsGroupNews.olimpiad_group_id == olimpiads_group_id).all(), key=lambda x: x.date)

        # Выбираем две последние новости
        news_in_rows = [all_news[:(min(len(all_news), 2))]]

        # Получаем расписание и заполняем его
        timetable = TimeTable(item.grades, item.subjects)
        for olimpiad in item.olimpiads:
            timetable.add(olimpiad.subject, olimpiad.grade, olimpiad.registration_data.date)

        # Получаем абзацы
        paragraphs = item.description.split('\n\n')
        return render_template("particular_olimpiad.html", olimpiad=item, subjects=subjects,
                               news=news_in_rows, timetable=timetable, paragraphs=paragraphs)

    @app.route('/tasks/<int:olimpiads_group_id>', methods=["GET", "POST"])
    def tasks(olimpiads_group_id):
        """Страница для получения заданий конкретной олимпиады"""

        # Загружаем группу олимпиад
        db_session = create_session()
        olimpiads_group = db_session.query(OlimpiadsGroup).filter(OlimpiadsGroup.id == olimpiads_group_id).first()

        if not olimpiads_group:
            abort(404)

        # Создаём форму с указанными предметами и классами
        form = data.forms.task_form.make_form(olimpiads_group.subjects, olimpiads_group.grades)

        if form.validate_on_submit():
            # Проверка на существование олимпиады

            res_olimp = db_session.query(Olimpiad).filter(Olimpiad.subject == form["subject"].data,
                                                          Olimpiad.grade == form["grade"].data,
                                                          Olimpiad.olimpiads_group_id == olimpiads_group_id).first()

            if res_olimp:
                return render_template("tasks.html", form=form, olimpiad=olimpiads_group, file=res_olimp.tasks)
            else:
                return render_template("tasks.html", form=form, olimpiad=olimpiads_group,
                                       message="Задания для такого предмета или класса не найдены")
        else:
            return render_template("tasks.html", form=form, olimpiad=olimpiads_group)

    @app.route('/add_olimp/<int:olimpiads_group_id>', methods=["GET", "POST"])
    @login_required
    def add_olimp(olimpiads_group_id):
        """Страница для добавления олимпиад у пользователя"""

        # Выбираем олимпиаду
        db_session = create_session()
        olimpiads_group = db_session.query(OlimpiadsGroup).filter(OlimpiadsGroup.id == olimpiads_group_id).first()

        if not olimpiads_group:
            abort(404)

        # Создаём форму с конкретными предметами, классами и городами
        form = data.forms.register_olimp_form.make_form(olimpiads_group.subjects,
                                                        olimpiads_group.grades,
                                                        olimpiads_group.cities)

        if form.validate_on_submit():
            subject = form['subject'].data
            grade = form['grade'].data

            # Получаем олимпиаду и пользователя (почему-то через current_user не работало)
            res_olimp = db_session.query(Olimpiad).filter(Olimpiad.olimpiads_group_id == olimpiads_group.id,
                                                          Olimpiad.subject == subject,
                                                          Olimpiad.grade == grade).first()
            user = db_session.query(User).filter(User.email == current_user.email).first()

            # Если мы нашли олимпиаду
            if res_olimp:
                user.olimpiads.append(res_olimp)
                db_session.commit()
                return redirect("/olimpiads")
            else:
                return render_template("register_olimp.html", form=form, olimpiad=olimpiads_group,
                                       message="Олимпиады по выбранным параметрам не найдено")

        return render_template("register_olimp.html", form=form, olimpiad=olimpiads_group)

    @app.route('/delete_olimp/<int:olimp_id>')
    @login_required
    def delete_olimp(olimp_id):
        """Страница для удаления олимпиад у пользователя"""

        db_session = create_session()

        # Выбираем пользователя и олимпиаду
        user = db_session.query(User).filter(User.email == current_user.email).first()
        olimp = db_session.query(Olimpiad).filter(Olimpiad.id == olimp_id).first()

        if not olimp:
            abort(404)

        user.olimpiads.remove(olimp)
        db_session.commit()

        return redirect('/user_olimpiads')

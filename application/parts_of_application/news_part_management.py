"""Этот файл предназначен для создания функций, связанных с новостями"""

# Импортируем необходимые файлы

# Загружаем класс таблицы новостей
from data.tables.olimpiads_group_news import OlimpiadsGroupNews

# Flask
from flask import render_template, abort

# Часть для работы с БД
from data.database.all_for_session import create_session


def init(app):

    @app.route('/', methods=["GET", "POST"])
    def news():
        """Главная страница для показа новостей"""

        # Выбираем все новости
        db_session = create_session()

        all_news = sorted(db_session.query(OlimpiadsGroupNews).all(), key=lambda x: x.date, reverse=True)
        news_in_rows = []

        # Делаем по три новости в ряду
        for i in range(0, len(all_news), 3):
            news_in_rows.append(all_news[i: min(len(all_news), i + 3)])

        return render_template("news.html", news=news_in_rows, title='Главная')

    @app.route('/particular_news/<int:news_id>')
    def particular_news(news_id):
        """Страница для отображения конкретной новости"""

        # Выбираем новость
        db_session = create_session()
        item = db_session.query(OlimpiadsGroupNews).filter(OlimpiadsGroupNews.id == news_id).first()

        if not item:
            abort(404)

        # Разбиваем её на параграфы
        paragraphs = item.text.split('\n\n')

        return render_template("particular_news.html", news=item, paragraphs=paragraphs, title=f'Новость: {item.title}')

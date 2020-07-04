# Импортируем файлы

# Для работы с БД
from data.database.all_for_session import create_session, global_init

# Для работы почты
from mailing import make_mailing_work
import threading
from data.tables.olimpiads_group import OlimpiadsGroup

# Функционал приложения
from parts_of_application import user_part_management
from parts_of_application import news_part_management
from parts_of_application import olimpiads_part_management
from parts_of_application import add_data_part_management
from configuration import get_app_and_login_manager

# Инициализируем все рабочие части приложения
app, login_manager = get_app_and_login_manager()
user_part_management.init(login_manager, app)
news_part_management.init(app)
olimpiads_part_management.init(app)

# Часть для добавления информации
add_data_part_management.init(app)


def main():
    global_init('db/olimpiads_manager.sqlite')
    db_session = create_session()

    # Два потока: первый - отправка напоминаний на почту, второй - основная работа программы
    t1 = threading.Thread(target=make_mailing_work, args=(db_session.query(OlimpiadsGroup).all(),))
    t2 = threading.Thread(target=app.run, args=('127.0.0.1', 8080,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


if __name__ == '__main__':
    main()

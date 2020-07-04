"""Этот файл предназначен для работы почты"""

import schedule
import datetime

# Импортируем специальные библиотеки для работы почты
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def choose_users(olimpiads_groups):
    """Перебирает олимпиады и нужным пользователям отправляет напоминание"""

    for olimpiads_group in olimpiads_groups:
        for olimpiad in olimpiads_group.olimpiads:

            # Получаем текущее время и дату олимпиады
            date = olimpiad.registration_data.date
            now = datetime.datetime.now()

            # Текст письма
            description = f'Олимпиада: {olimpiads_group.name}, Предмет: {olimpiad.subject}, Класс: {olimpiad.grade}, ' \
                          f'Дата: {olimpiad.registration_data.date.strftime("%d %B")}'

            # Предупреждаем за два дня
            if date - now < two_days and olimpiad.users:
                send_messages(olimpiad.users, templates['two_days'] + f' {description}')


def send_messages(users, message):
    """Отправляет сообщения"""

    # Здесь надо указать логин и пароль от почты, с которой будут отправляться сообщения
    smtp_server = 'smtp.gmail.com'
    login = LOGIN
    password = PASSWORD

    # Список получателей
    recipients = [user.email for user in users]

    # Формируем структуру письма
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['Subject'] = Header('Напоминание об олимпиаде', 'utf-8')
    msg['From'] = login

    # Создаём специальный объект для отправки письма
    sender = smtplib.SMTP(smtp_server, 587)
    sender.starttls()
    sender.login(login, password)

    sender.sendmail(msg['From'], recipients, msg.as_string())
    sender.quit()


def make_mailing_work(groups):
    """Каждый день идет проверка"""
    schedule.every(1).days.do(choose_users, olimpiads_groups=groups)

    while True:
        schedule.run_pending()


# Шаблоны для письма
templates = {'one_day': "Тут будет нормальное напоминание о олимпиаде, которая состоится через 1 день.",
             'two_days': "Тут будет нормальное напоминание о олимпиаде, которая состоится через 2 дня.",
             'week': "Тут будет нормальное напоминание о олимпиаде, которая состоится через неделю."}

# Временной промежуток в два дня
two_days = datetime.timedelta(days=2)

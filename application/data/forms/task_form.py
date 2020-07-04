from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


def make_form(subjects, grades):
    """Возвращает форму с указанными предметами и классами"""

    class TaskForm(FlaskForm):
        """Форма для получения заданий олимпиады"""

        subject = SelectField("Предмет", choices=[(i, i) for i in subjects.split(', ')])
        grade = SelectField("Ваш класс", choices=[(i, i) for i in grades.split(', ')])
        submit = SubmitField("Скачать задания")

    return TaskForm()

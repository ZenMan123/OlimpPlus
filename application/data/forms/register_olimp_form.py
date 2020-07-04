from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField


def make_form(subjects, grades, cities):
    """Возвращает форму с указанными вариантами select элемента"""

    class RegisterOlimpForm(FlaskForm):
        """Форма для участия в олимпиаде"""

        subject = SelectField('Предмет', choices=[(i, i) for i in subjects.split(', ')])
        grade = SelectField('Класс', choices=[(i, i) for i in grades.split(', ')])
        city = SelectField('Город', choices=[(i, i) for i in cities.split(', ')])
        submit = SubmitField("Участвовать")

    return RegisterOlimpForm()

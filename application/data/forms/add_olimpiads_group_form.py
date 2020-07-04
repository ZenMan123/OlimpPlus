from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectMultipleField, TextAreaField, widgets
from wtforms.validators import InputRequired

# Импортируем список городов, предметов, классов
from useful_things import SUBJECTS, CITIES, GRADES


# Этот класс реализует чекбоксы в flask-wtf
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddOlimpiadsGroupForm(FlaskForm):
    """Форма для добавления олимпиад админом"""

    name = StringField("Имя группы", validators=[InputRequired(message="Вы не заполнили это поле")])
    organizer = StringField("Организатор", validators=[InputRequired(message="Вы не заполнили это поле")])
    description = TextAreaField("Описание", validators=[InputRequired(message="Вы не заполнили это поле")])

    subjects = MultiCheckboxField("Предметы", choices=SUBJECTS)
    grades = MultiCheckboxField("Классы", choices=GRADES)
    cities = MultiCheckboxField("Города", choices=CITIES)
    extra_cities = StringField("Добавить города (перечислить через запятую)")

    link = StringField("Ссылка на официальный сайт", validators=[InputRequired(message="Вы не заполнили это поле")])
    photo = FileField("Фотография")
    submit = SubmitField("Добавить")

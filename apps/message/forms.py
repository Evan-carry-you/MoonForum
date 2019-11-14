from wtforms_tornado import Form
from wtforms import StringField, IntegerField
from wtforms.validators import AnyOf, DataRequired, Length


class MessageForm(Form):
	receiver = IntegerField("接收者", validators=[DataRequired(message="请传入接收者")])

from wtforms_tornado import Form
from wtforms import StringField, IntegerField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, length, AnyOf


class QuestionForm(Form):
	category = StringField(validators=[DataRequired(message="请选择问题分类"), AnyOf(values=["技术回答", "技术分享", "活动建议"])])
	title = StringField(validators=[DataRequired(message="请输入问题")])
	content = TextAreaField(validators=[DataRequired(message="请输入问题描述")])


class AnswerForm(Form):
	content = StringField(validators=[DataRequired(message="请输入回答内容")])


class ReplyForm(Form):
	content = StringField(validators=[DataRequired(message="请输入回复内容")])
	replyed_user = IntegerField(validators=[DataRequired(message="请传入被回复者")])

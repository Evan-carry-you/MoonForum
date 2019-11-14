from wtforms_tornado import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Length, AnyOf

MOBILE_REGEX = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$|^186\d{8}$"


class SMSCodeForm(Form):
	mobile = StringField("手机号", validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])

class RegisterForm(Form):
	mobile = StringField("手机号", validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])
	code = StringField("验证码", validators=[DataRequired(message="请输入验证码"), Length(max=4,min=4, message="验证码是四位数字")])
	password = StringField("密码", validators=[DataRequired(message="请输入密码")])

class LoginForm(Form):
	mobile = StringField("手机号", validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])
	password = StringField("密码", validators=[DataRequired(message="请输入密码")])

class InfoForm(Form):
	nick_name = StringField("昵称", validators=[DataRequired(message="请输入昵称"), Length(max=20, min=2, message="长度必须在5到20个字符之间")])
	gender = StringField("性别", validators=[DataRequired(message="请选择性别"), AnyOf(values=["male", "female"])])
	address = StringField("地址", validators=[DataRequired(message="请输入地址")])
	desc = TextAreaField("简介", validators=[])

class PasswordForm(Form):
	old_password = StringField("旧密码", validators=[DataRequired(message="请输入旧密码")])
	new_password = StringField("新密码", validators=[DataRequired(message="请输入新密码")])
	confirm_password = StringField("确认", validators=[DataRequired(message="再输入一次新密码")])

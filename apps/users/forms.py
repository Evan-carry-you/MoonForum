from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Regexp, Length

MOBILE_REGEX = "^1[358]\d{9}$|^147\d{8}$|^176\d{8}$|^186\d{8}$"


class SMSCodeForm(Form):
	mobile = StringField("手机号", validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])

class RegisterForm(Form):
	mobile = StringField("手机号", validators=[DataRequired(message="请输入手机号码"), Regexp(MOBILE_REGEX, message="请输入合法的手机号码")])
	code = StringField("验证码", validators=[DataRequired(message="请输入验证码"), Length(max=4,min=4, message="验证码是四位数字")])
	password = StringField("密码", validators=[DataRequired(message="请输入密码")])

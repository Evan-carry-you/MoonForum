from wtforms_tornado import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Regexp, AnyOf

class CommunityGroupForm(Form):
	name = StringField("小组名称", validators=[DataRequired(message="请输入小组名称")])
	category = StringField("小组分类", validators=[AnyOf(values=["教育同盟", "同城交易", "程序设计", "生活兴趣"])])
	desc = TextAreaField("小组简介", validators=[DataRequired(message="请输入简介")])
	notice = TextAreaField("小组公告", validators=[DataRequired(message="请输入公告")])

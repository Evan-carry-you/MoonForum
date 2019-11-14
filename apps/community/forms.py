from wtforms_tornado import Form
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Regexp, AnyOf, length

class CommunityGroupForm(Form):
	name = StringField("小组名称", validators=[DataRequired(message="请输入小组名称")])
	category = StringField("小组分类", validators=[AnyOf(values=["教育同盟", "同城交易", "程序设计", "生活兴趣"])])
	desc = TextAreaField("小组简介", validators=[DataRequired(message="请输入简介")])
	notice = TextAreaField("小组公告", validators=[DataRequired(message="请输入公告")])

class CommunityApplyForm(Form):
	apply_reason = StringField("申请理由", validators=[DataRequired("请输入申请理由")])

class PostForm(Form):
	title = StringField("标题", validators=[DataRequired("请输入标题")])
	content = StringField("内容", validators=[DataRequired("内容")])

class CommentForm(Form):
	content = StringField("评论内容", validators=[DataRequired(message="请输入评论内容"), length(min=5, message="不能少于5个字符")])

class CommentReplyForm(Form):
	replyed_user = IntegerField("回复用户", validators=[DataRequired("请输入回复用户")])
	content = StringField("回复", validators=[DataRequired(message="请输入回复内容"), length(min=5, message="不能少于5个字符")])

class HandleApplyForm(Form):
	status = StringField("审核状态", validators=[DataRequired(message="请传入审核状态"), AnyOf(values=["agree", "refuse"])])
	handle_msg = StringField("处理原因")


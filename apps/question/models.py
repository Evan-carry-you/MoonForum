from peewee import CharField, TextField, IntegerField, ForeignKeyField, JOIN

from MoonForum.models import BaseModel
from apps.users.models import User


class Question(BaseModel):
	user = ForeignKeyField(User, verbose_name="提问者")
	category = CharField(max_length=40, verbose_name="问题分类")
	title = CharField(max_length=144, verbose_name="问题标题")
	content = TextField(verbose_name="问题详情")
	image = CharField(null=True, verbose_name="图片")
	answer_nums = IntegerField(default=0, verbose_name="回答数量")

	@classmethod
	def extend(cls):
		return cls().select(cls, User.id, User.nick_name).join(User)


class Answer(BaseModel):
	user = ForeignKeyField(User, verbose_name="回答者")
	question = ForeignKeyField(Question,null=True, verbose_name="回答的问题")
	parent_answer = ForeignKeyField('self', null=True, verbose_name="回复回答")
	reply_user = ForeignKeyField(User, null=True, verbose_name="回复用户")
	content = TextField(verbose_name="回答内容")
	reply_nums = IntegerField(verbose_name="回复数量", default=0)

	@classmethod
	def extend(cls):
		answerer = User.alias()
		replier = User.alias()
		return cls().select(cls, answerer.id, answerer.nick_name, replier.id, replier.nick_name).join(
			Question, join_type=JOIN.LEFT_OUTER, on=cls.question
		).switch(cls).join(
			answerer, join_type=JOIN.LEFT_OUTER, on=cls.user
		).switch(cls).join(
			replier, join_type=JOIN.LEFT_OUTER, on=cls.reply_user
		)

from datetime import datetime

from peewee import *


from MoonForum.models import BaseModel
from apps.users.models import User

class CommunityGroup(BaseModel):
	add_user = ForeignKeyField(User, verbose_name="小组创建者", index=True)
	name = CharField(max_length=64, null=True, verbose_name="小组名", index=True)
	category = CharField(max_length=20, verbose_name="小组分类", null=True)
	front_image = CharField(max_length=200, verbose_name="封面图", null=True)
	desc =TextField(verbose_name="简介")
	notice = TextField(verbose_name="公告")
	member_nums = IntegerField(verbose_name="小组成员数", default=0)
	post_nums = IntegerField(verbose_name="小组帖子数", default=0)

	@classmethod
	def extend(cls):
		return cls().select(cls, User.id, User.nick_name).join(User)

HANDLE_STATUS = (
	("agree", "同意"),
	("refuse", "拒绝")
)

class CommunityGroupMember(BaseModel):
	user = ForeignKeyField(User, verbose_name="成员名")
	community = ForeignKeyField(CommunityGroup, verbose_name="社区")
	status = CharField(choices=HANDLE_STATUS, verbose_name="处理状态", null=True, max_length=10)
	handle_msg = CharField(max_length=200, null=True, verbose_name="处理内容")
	apply_reason = CharField(max_length=200, verbose_name="申请原因")
	handle_time = DateField(default=datetime.now(), verbose_name="处理时间")

	@classmethod
	def extend(cls):
		return cls().select(cls, User.id, User.nick_name, User.head , CommunityGroup).join(User).switch(cls).join(CommunityGroup)

class Post(BaseModel):
	user = ForeignKeyField(User, verbose_name="作者")
	title = CharField(max_length=200, verbose_name="标题")
	group = ForeignKeyField(CommunityGroup, verbose_name="小组")
	content = TextField(verbose_name="内容")
	comment_nums = IntegerField(verbose_name="评论数", default=0)
	is_excellent = BooleanField(default=0, verbose_name="是否精华")
	is_hot = BooleanField(default=0, verbose_name="是否热门")

	@classmethod
	def extend(cls):
		return cls.select(cls, User.id, User.nick_name).join(User)

class PostComment(BaseModel):
	user = ForeignKeyField(User, verbose_name="用户", related_name="author")
	post = ForeignKeyField(Post, null=True, verbose_name="帖子")
	parent_comment = ForeignKeyField('self', null=True, verbose_name="回复的评论")
	replied_user = ForeignKeyField(User, verbose_name="回复对象", related_name="replied_user", null=True)
	content = CharField(max_length=400, verbose_name="内容")
	replied_nums = IntegerField(verbose_name="回复数量", default=0)
	like_nums = IntegerField(verbose_name="点赞数量", default=0)

	@classmethod
	def extend(cls):
		author = User.alias()
		replied_user = User.alias()

		return cls.select(cls, Post, author.id, author.nick_name, replied_user.id, replied_user.nick_name).join(
			Post, join_type=JOIN.LEFT_OUTER, on=cls.post
		).switch(cls).join(
			author, join_type=JOIN.LEFT_OUTER, on=cls.user
		).switch(cls).join(
			replied_user, join_type=JOIN.LEFT_OUTER, on=cls.replied_user
		)

class CommentsLike(BaseModel):
	user = ForeignKeyField(User, verbose_name="用户")
	post_comment = ForeignKeyField(PostComment, verbose_name="帖子")


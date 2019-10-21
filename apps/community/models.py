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
	member_numbers = IntegerField(verbose_name="小组成员数", default=0)
	post_number = IntegerField(verbose_name="小组帖子数", default=0)

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
	apply_reason = CharField(max_length=200, verbose_name="处理原因")
	handle_time = CharField(max_length=200, verbose_name="处理时间")

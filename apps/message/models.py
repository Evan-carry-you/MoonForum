from peewee import CharField, IntegerField, ForeignKeyField

from MoonForum.models import BaseModel
from apps.users.models import User

MESSAGE_TYPE = (
	(1, "评论"),
	(2, "帖子回复"),
	(3, "点赞"),
	(4, "回答"),
	(5, "回答回复"),
)


class Message(BaseModel):
	sender = ForeignKeyField(User, verbose_name="消息发送者")
	receiver = ForeignKeyField(User, verbose_name="消息接收者")
	message_type = IntegerField(choices=MESSAGE_TYPE, verbose_name="消息类型")
	message = CharField(max_length=200, null=True, verbose_name="消息内容")
	parent_content = CharField(max_length=200, null=True, verbose_name="被回复的内容")

from datetime import datetime

from peewee import *
from peewee import Model

from MoonForum.settings import database

class BaseModel(Model):
	add_time = DateField(default=datetime.now, verbose_name="添加时间")

	class Meta:
		database = database

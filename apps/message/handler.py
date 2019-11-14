import json
from playhouse.shortcuts import model_to_dict

from MoonForum.handler import RedisHandler
from apps.utils.moon_decorators import authenticated_async
from apps.message.models import Message
from apps.users.models import User
from apps.community.models import CommunityGroupMember, CommunityGroup


class MessageHandler(RedisHandler):
	@authenticated_async
	async def get(self, *args, **kwargs):
		re_data = []
		type_list = self.get_query_arguments("message_type", [])
		if type_list:
			message_query = Message.select().order_by(Message.add_time.desc()).filter(
				Message.receiver_id == self.current_user.id, Message.message_type.in_(type_list))
		else:
			message_query = Message.filter(Message.receiver_id == self.current_user.id)
		messages = await self.application.objects.execute(message_query)

		for message in messages:
			sender = await self.application.objects.get(User, id=message.sender_id)
			re_data.append({
				"sender":         {
					"id":        sender.id,
					"nick_name": sender.nick_name,
					"head_url":  '/{}/{}'.format(self.settings['MEDIA_DIR'], sender.head)
				},
				"message":        message.message,
				"message_type":   message.message_type,
				"parent_content": message.parent_content,
				"add_time":       message.add_time.strftime("%Y-%m-%d %H:%M:%S")
			})

		self.finish(json.dumps(re_data))



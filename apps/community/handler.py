import os
import uuid
import json

import aiofiles
from playhouse.shortcuts import model_to_dict

from MoonForum.handler import RedisHandler
from apps.utils.moon_decorators import authenticated_async
from apps.community.models import CommunityGroup
from apps.community.forms import CommunityGroupForm
from apps.utils.util_funcs import json_serial


class GroupHandler(RedisHandler):
	async def get(self, *args, **kwargs):
		re_data = []
		community_query = CommunityGroup.extend()
		# 默认请求
		c = self.get_argument('c', None)
		if c:
			# 按分类查询
			if c == "new":
				community_query = community_query.order_by(CommunityGroup.add_time.desc())
			else:
				community_query = community_query.filter(CommunityGroup.category==c)
		order = self.get_argument('o', None)
		# 时间排列
		if order:
			if order == "new":
				community_query = community_query.order_by(CommunityGroup.add_time.desc())
			elif order == "hot":
				community_query = community_query.order_by(CommunityGroup.member_numbers.desc())
		limit = self.get_argument('limit', None)
		if limit:
			community_query = community_query.limit(int(limit))
		groups = await self.application.objects.execute(community_query)
		for group in groups:
			group_dict = model_to_dict(group)
			group_dict['front_image'] = "{web_url}/{media}/{front_image}".format(web_url=self.settings['WEB_URL'], media=self.settings['MEDIA_DIR'], front_image=group_dict['front_image'])
			re_data.append(group_dict)
		self.finish(json.dumps(re_data, default=json_serial))





	@authenticated_async
	async def post(self, *args, **kwargs):
		re_data = {}

		group_form = CommunityGroupForm(self.request.body_arguments)
		if group_form.validate():
			files_meta = self.request.files.get("front_image", None)
			if not files_meta:
				self.set_status(400)
				re_data['front_image'] = "请上传图片"
			else:
				# 上传图片
				new_filename = ""
				for meta in files_meta:
					filename = meta['filename']
					new_filename = "{uuid}_{filename}".format(uuid=uuid.uuid4(), filename=filename)
					file_path= os.path.join(self.settings['MEDIA_ROOT'], new_filename)
				async with aiofiles.open(file_path, 'wb') as f:
						await f.write(meta['body'])
				# 写入数据库
				group = await self.application.objects.create(CommunityGroup, add_user=self.current_user, name=group_form.name.data,
				                                             category=group_form.category.data, desc=group_form.desc.data,
				                                             notice=group_form.notice.data, front_image=new_filename)
				re_data['id'] = group.id
		else:
			self.set_status(400)
			for field in group_form:
				re_data[field] = group_form.errors[field][0]
		self.finish(re_data)

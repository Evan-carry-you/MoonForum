import os
import uuid
import json

import aiofiles
from playhouse.shortcuts import model_to_dict

from MoonForum.handler import RedisHandler
from apps.users.models import User
from apps.utils.moon_decorators import authenticated_async
from apps.community.models import CommunityGroup, CommunityGroupMember, Post, PostComment, CommentsLike
from apps.community.forms import *
from apps.utils.util_funcs import json_serial
from apps.message.models import Message


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
				community_query = community_query.filter(CommunityGroup.category == c)
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
			group_dict['front_image'] = "{web_url}/{media}/{front_image}".format(web_url=self.settings['WEB_URL'],
			                                                                     media=self.settings['MEDIA_DIR'],
			                                                                     front_image=group_dict['front_image'])
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
					file_path = os.path.join(self.settings['MEDIA_ROOT'], new_filename)
				async with aiofiles.open(file_path, 'wb') as f:
					await f.write(meta['body'])
				# 写入数据库
				group = await self.application.objects.create(CommunityGroup, add_user=self.current_user,
				                                              name=group_form.name.data,
				                                              category=group_form.category.data, desc=group_form.desc.data,
				                                              notice=group_form.notice.data, front_image=new_filename)
				re_data['id'] = group.id
		else:
			self.set_status(400)
			for field in group_form:
				re_data[field] = group_form.errors[field][0]
		self.finish(re_data)


class GroupMemberHandler(RedisHandler):
	@authenticated_async
	async def post(self, group_id, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf8")
		param = json.loads(param)

		community_apply_form = CommunityApplyForm.from_json(param)

		if community_apply_form.validate():
			# 判断是否有这个小组
			try:
				group = await self.application.objects.get(CommunityGroup, id=int(group_id))

				existed = await self.application.objects.get(CommunityGroupMember, community=group, user=self.current_user)
				self.set_status(400)
				re_data['non_fields'] = "用户已经加入了！"

			except CommunityGroup.DoesNotExist as e:
				self.set_status(404)
			except CommunityGroupMember.DoesNotExist as e:
				community_member = await self.application.objects.create(CommunityGroupMember, community=group,
				                                                         user=self.current_user,
				                                                         apply_reason=community_apply_form.apply_reason.data)
				re_data['id'] = community_member.id
		# 申请通知
		# await self.application.objects.create(Message, sender=self.current_user, receiver=receiver, message_type=4,
		# 																			message="", parent_content=comment.content)
		else:
			self.set_status(400)
			for field in community_apply_form.erros:
				re_data[field] = community_apply_form.errors[field][0]
		self.finish(re_data)


class GroupDetailHandler(RedisHandler):
	@authenticated_async
	async def get(self, group_id, *args, **kwargs):
		re_data = {}
		try:
			group = await self.application.objects.get(CommunityGroup, id=group_id)

			item_dict = {}
			item_dict['name'] = group.name
			item_dict['category'] = group.category
			item_dict['front_image'] = '{}/{}/{}'.format(self.settings['WEB_URL'], self.settings['MEDIA_DIR'],
			                                             group.front_image)
			item_dict['desc'] = group.desc
			item_dict['notice'] = group.notice
			item_dict['member_nums'] = group.member_nums
			item_dict['post_nums'] = group.post_nums

			re_data = item_dict
		except CommunityGroup.DoesNotExist as e:
			self.set_status(404)
		self.finish(re_data)


class PostHandler(RedisHandler):
	@authenticated_async
	async def get(self, group_id, *args, **kwargs):
		post_list = []

		try:
			group = await self.application.objects.get(CommunityGroup, id=int(group_id))
			group_member = await self.application.objects.get(CommunityGroupMember, community=group, status="agree")

			posts_query = Post.extend()
			c = self.get_argument("cate", None)
			if c:
				if c == "精华帖子":
					posts_query = posts_query.filter(Post.is_excellent == True)
				if c == "hot":
					posts_query = posts_query.filter(Post.is_hot == True)

			posts = await self.application.objects.execute(posts_query)

			for post in posts:
				post_dict = {
					"user":    {
						"id":        post.user.id,
						"nick_name": post.user.nick_name
					},
					"id":      post.id,
					"title":   post.title,
					"content": post.content,
				}
				post_list.append(post_dict)

		except CommunityGroup.DoesNotExist as e:
			self.set_status(404)
		except CommunityGroupMember.DoesNotExist as e:
			self.set_status(403)

		self.finish(json.dumps(post_list))

	@authenticated_async
	async def post(self, group_id, *args, **kwargs):
		re_data = {}
		try:
			group = await self.application.objects.get(CommunityGroup, id=int(group_id))
			group_member = await self.application.objects.get(CommunityGroupMember, user=self.current_user, community=group,
			                                                  status="agree")

			param = self.request.body.decode("utf8")
			param = json.loads(param)

			post_form = PostForm.from_json(param)
			if post_form.validate():
				post = await self.application.objects.create(Post, title=post_form.title.data, content=post_form.content.data,
				                                             group=group, comment_nums=0, user=self.current_user)
				re_data['id'] = post.id
			else:
				for field in post_form.errors:
					re_data[field] = post_form.errors[field][0]

		except CommunityGroup.DoesNotExist as e:
			self.set_status(404)
		except CommunityGroupMember.DoesNotExist as e:
			self.set_status(403)
		self.finish(re_data)


class PostDetailHandler(RedisHandler):
	@authenticated_async
	async def get(self, post_id, *args, **kwargs):
		re_data = {}

		try:
			group_member = await self.application.objects.get(CommunityGroupMember, user=self.current_user)
			post_details = await self.application.objects.execute(Post.extend().where(Post.id == int(post_id)))
			re_count = 0
			for data in post_details:
				re_data['user'] = model_to_dict(data.user)
				re_data['title'] = data.title
				re_data['content'] = data.content
				re_data['date'] = data.add_time.strftime("%Y-%m-%d")
				re_data['comment_nums'] = data.comment_nums
				re_count += 1
			if re_count < 1:
				self.set_status(404)
		except CommunityGroupMember.DoesNotExist as e:
			self.set_status(403)

		self.finish(re_data)


class PostCommentHandler(RedisHandler):
	@authenticated_async
	async def get(self, post_id, *args, **kwargs):
		# 从数据库中取出 post 为 post_id 且 parent_comment 是 null 的 comment
		re_data = []
		try:
			post = await self.application.objects.get(Post, id=int(post_id))
			comment_query = PostComment.extend().where(PostComment.post == post,
			                                           PostComment.parent_comment.is_null(True)).order_by(
				PostComment.add_time.desc())
			comments = await self.application.objects.execute(comment_query)

			for comment in comments:
				has_liked = False
				try:
					comments_like = await self.application.objects.get(CommentsLike, post_comment_id=comment.id)
					has_liked = True
				except CommentsLike.DoesNotExist as e:
					pass
				comment_dict = {
					"user":         model_to_dict(comment.user),
					"content":      comment.content,
					"has_liked":    has_liked,
					"replied_nums": comment.replied_nums,
					"like_nums":    comment.like_nums,
					"id":           comment.id
				}
				re_data.append(comment_dict)
		except Post.DoesNotExist as e:
			self.set_status(404)
		self.finish(json.dumps(re_data, default=json_serial))

	@authenticated_async
	async def post(self, post_id, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf8")
		param = json.loads(param)

		comment_form = CommentForm.from_json(param)
		if comment_form.validate():
			try:
				post = await self.application.objects.get(Post, id=int(post_id))
				comment = await self.application.objects.create(PostComment, user=self.current_user,
				                                                post=post, content=comment_form.content.data)
				re_data['id'] = comment.id
				re_data['user'] = {}
				re_data['user']['id'] = self.current_user.id
				re_data['user']['nick_name'] = self.current_user.nick_name
				# 写入回复通知
				receiver = await self.application.objects.get(User, id=post.user_id)
				await self.application.objects.create(Message, sender=self.current_user, receiver=receiver, message_type=1,
				                                      message=comment_form.content.data, parent_content=post.title)
				post.comment_nums += 1
				await self.application.objects.update(post)
			except Post.DoesNotExist as e:
				self.set_status(404)
		else:
			self.set_status(400)
			for field in comment_form.erros:
				re_data[field] = comment_form.errors[field][0]

		self.finish(json.dumps(re_data))


class CommentReplyHandler(RedisHandler):
	@authenticated_async
	async def get(self, comment_id, *args, **kwargs):
		re_data = []
		try:
			replies = await self.application.objects.execute(
				PostComment.extend().where(PostComment.parent_comment == int(comment_id)).order_by(PostComment.add_time.desc()))
			for item in replies:
				item_dict = dict()
				item_dict['content'] = item.content
				item_dict['user'] = model_to_dict(item.user)
				item_dict['add_time'] = item.add_time.strftime("%Y-%m-%d")
				item_dict['id'] = item.id
				item_dict['reply_nums'] = item.replied_nums
				re_data.append(item_dict)
		except PostComment.DoesNotExist as e:
			self.set_status(404)
		self.finish(json.dumps(re_data))

	@authenticated_async
	async def post(self, comment_id, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf8")
		param = json.loads(param)
		reply_form = CommentReplyForm.from_json(param)

		if reply_form.validate():
			try:
				comment = await self.application.objects.get(PostComment, id=int(comment_id))
				replied_user = await self.application.objects.get(User, id=reply_form.replyed_user.data)
				reply = await self.application.objects.create(PostComment, user=self.current_user, parent_comment=comment,
				                                              replied_user=replied_user, content=reply_form.content.data)
				comment.replied_nums += 1
				await self.application.objects.update(comment)
				re_data['id'] = reply.id
				# 写入回复通知
				await self.application.objects.create(Message, sender=self.current_user, receiver=replied_user, message_type=2,
				                                      message=reply_form.content.data, parent_content=comment.content)

			except PostComment.DoesNotExist as e:
				self.set_status(404)
			except User.DoesNotExist as e:
				self.set_status(400)
				re_data['repied_user'] = "用户不存在"
		else:
			self.set_status(400)
			for field in reply_form.errors:
				re_data[field] = reply_form.errors[field][0]
		self.finish(re_data)


class CommentLikeHandler(RedisHandler):
	@authenticated_async
	async def post(self, comment_id, *args, **kwargs):
		re_data = {}

		try:
			user = await self.application.objects.get(User, id=self.current_user)
			comment = await self.application.objects.get(PostComment, id=int(comment_id))
			comment_like = await self.application.objects.get(CommentsLike, post_comment=comment_id, user=self.current_user)
		except User.DoesNotExist as e:
			self.set_status(400)
		except PostComment.DoesNotExist as e:
			self.set_status(404)
		except CommentsLike.DoesNotExist as e:
			# 之前没有被点赞过，加入点赞
			comment_like = await self.application.objects.create(CommentsLike, post_comment=comment, user=user)
			re_data['id'] = comment_like.id
			# 写入点赞通知
			receiver = await self.application.objects.get(User, id=comment.user_id)
			await self.application.objects.create(Message, sender=self.current_user, receiver=receiver, message_type=3,
			                                      message="", parent_content=comment.content)
			comment.like_nums += 1
			await self.application.objects.update(comment)
		self.finish(re_data)


class ApplyHandler(RedisHandler):
	@authenticated_async
	async def get(self, *args, **kwargs):
		re_data = []
		all_groups = await self.application.objects.execute(
			CommunityGroup.extend().where(CommunityGroup.add_user == self.current_user))
		all_group_ids = [group.id for group in all_groups]
		group_member_query = CommunityGroupMember.extend().where(CommunityGroupMember.community_id.in_(all_group_ids),
		                                                         CommunityGroupMember.status.is_null(True))
		group_members = await self.application.objects.execute(group_member_query)
		for member in group_members:
			re_data.append({
				"id":           member.id,
				"user":         {
					"id":        member.user.id,
					"nick_name": member.user.nick_name
				},
				"group":        member.community.name,
				"apply_reason": member.apply_reason,
				"add_time":     member.add_time.strftime("%Y-%m-%m")
			})
		self.finish(json.dumps(re_data))


class HandleApplyHandler(RedisHandler):
	@authenticated_async
	async def patch(self, apply_id, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf8")
		param = json.loads(param)
		form = HandleApplyForm.from_json(param)

		if form.validate():
			all_group = await self.application.objects.execute(
				CommunityGroup.extend().where(CommunityGroup.add_user == self.current_user))
			apply = await self.application.objects.execute(
				CommunityGroupMember.extend().where(CommunityGroupMember.id == apply_id,
				                                    CommunityGroupMember.status.is_null(True)))
			group_ids = [group.id for group in all_group]
			count = 0
			for app in apply:
				if app.community.id in group_ids:
					# 修改处理结果，并更新最终信息
					app.status = form.status.data
					app.handle_msg = form.handle_msg.data
					await self.application.objects.update(app)
					re_data['success'] = 1
					count += 1
				else:
					self.set_status(403)
			if count == 0:
				self.set_status(400)
		else:
			for field in form.errors:
				re_data[field] = form.errors[field][0]

		self.finish(re_data)

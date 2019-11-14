import uuid
import os
import json
from playhouse.shortcuts import model_to_dict

import aiofiles

from MoonForum.handler import RedisHandler
from apps.question.forms import QuestionForm, AnswerForm, ReplyForm
from apps.question.models import Question, Answer
from apps.utils.moon_decorators import authenticated_async
from apps.utils.util_funcs import json_serial
from apps.message.models import Message
from apps.users.models import User


class QuestionHandler(RedisHandler):
	# @authenticated_async
	async def get(self, *args, **kwargs):
		re_data = []

		# params = self.request.body.decode("utf8")
		# params = json.loads(params)

		order = self.get_argument("o", None)
		category = self.get_argument("c", None)

		question_query = Question.extend()
		if order:
			if order == "hot":
				question_query = question_query.order_by(Question.answer_nums.desc())
			if order == "new":
				question_query = question_query.order_by(Question.id.desc())
		else:
			question_query = question_query.order_by(Question.id.desc())
		if category:
			question_query = question_query.filter(Question.category == category)

		questions = await self.application.objects.execute(question_query)
		for question in questions:
			question_dict = model_to_dict(question)
			re_data.append(question_dict)
		self.finish(json.dumps(re_data, default=json_serial))

	@authenticated_async
	async def post(self, *args, **kwargs):
		re_data = {}

		question_form = QuestionForm(self.request.body_arguments)

		if question_form.validate():
			files_meta = self.request.files.get("image", None)
			if not files_meta:
				self.set_status(400)
				re_data['image'] = "请上传图片"
			else:
				new_filename = ""
				for meta in files_meta:
					filename = meta['filename']
					new_filename = "{uuid}_{filename}".format(uuid=uuid.uuid4(), filename=filename)
					file_path = os.path.join(self.settings['MEDIA_ROOT'], new_filename)
					async with aiofiles.open(file_path, "wb") as f:
						await f.write(meta['body'])
				question = await self.application.objects.create(Question, user=self.current_user,
				                                                 category=question_form.category.data,
				                                                 title=question_form.title.data,
				                                                 content=question_form.content.data,
				                                                 image=new_filename)
				re_data["id"] = question.id
		else:
			for field in question_form.errors:
				re_data[field] = question_form.errors[field][0]

		self.finish(re_data)


class QuestionDetailHandler(RedisHandler):
	async def get(self, question_id, *args, **kwargs):
		re_data = {}

		question_query = Question.extend().where(Question.id == int(question_id))
		question = await self.application.objects.execute(question_query)
		question_count = 0
		for item in question:
			re_data = model_to_dict(item)
			question_count += 1
			re_data['image'] = "{web_url}/{media}/{image}".format(web_url=self.settings['WEB_URL'],
			                                                      media=self.settings['MEDIA_DIR'],
			                                                      image=re_data['image'])
		if question_count == 0:
			self.set_status(404)

		self.finish(json.dumps(re_data, default=json_serial))


class AnswerHandler(RedisHandler):
	async def get(self, question_id, *args, **kwargs):
		re_data = []
		try:
			question = await self.application.objects.get(Question, id=int(question_id))
			answer_query = Answer.extend().where(Answer.question == question, Answer.parent_answer.is_null(True))
			answers = await self.application.objects.execute(answer_query)
			count = 0
			# question = ForeignKeyField(Question, verbose_name="回答的问题")
			# parent_answer = ForeignKeyField('self', null=True, verbose_name="回复回答")
			# reply_user = ForeignKeyField(User, null=True, verbose_name="回复用户")
			# content = TextField(verbose_name="回答内容")
			# reply_nums = IntegerField(verbose_name="回复数量", default=0)
			for answer in answers:
				answer_dict = {
					"id":         answer.id,
					"user":       model_to_dict(answer.user),
					"reply_user": model_to_dict(answer.reply_user),
					"content":    answer.content,
					"reply_nums": answer.reply_nums,
					"add_time":   answer.add_time.strftime("%Y-%m-%d")
				}
				re_data.append(answer_dict)
				count += 1
			if count == 0:
				self.set_status(404)
		except Question.DoesNotExist as e:
			self.set_status(404)
		self.finish(json.dumps(re_data, default=json_serial))

	@authenticated_async
	async def post(self, question_id, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf8")
		param = json.loads(param)
		answer_form = AnswerForm.from_json(param)

		if answer_form.validate():
			questions = await self.application.objects.execute(Question.extend().where(Question.id == int(question_id)))
			count = 0
			for question in questions:
				answer = await self.application.objects.create(Answer, user=self.current_user, content=answer_form.content.data,
				                                               question=question, reply_user=question.user)
				count += 1
				re_data['id'] = answer.id
				receiver = await self.application.objects.get(User, id=question.user)
				await self.application.objects.create(Message, sender=self.current_user, receiver=receiver, message_type=4,
																							message=answer_form.content.data, parent_content=question.title)
			if count == 0:
				self.set_status(404)
		else:
			for field in answer_form.errors:
				re_data[field] = answer_form.errors[field][0]

		self.finish(re_data)


class ReplyHandler(RedisHandler):
	@authenticated_async
	async def post(self, answer_id, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf8")
		param = json.loads(param)
		reply_form = ReplyForm.from_json(param)

		if reply_form.validate():
			answer = await self.application.objects.execute(Answer.extend().where(Answer.id == int(answer_id)))
			count = 0
			for item in answer:
				try:
					reply_user = await self.application.objects.get(User, id=int(reply_form.replyed_user.data))
					reply = await self.application.objects.create(Answer, user=self.current_user, content=reply_form.content.data,
																												reply_user=reply_user, parent_answer=item)
					count += 1
					item.reply_nums += 1
					await self.application.objects.update(item)
					re_data['id'] = reply.id
					await self.application.objects.create(Message, sender=self.current_user, receiver=reply_user, message_type=5,
																								message=reply_form.content.data, parent_content=item.content)
				except User.DoesNotExist as e:
					self.set_status(400)
			if count == 0:
				self.set_status(400)
		else:
			for field in reply_form.errors:
				re_data[field] = reply_form.errors[field][0]
		self.finish(re_data)

	async def get(self, answer_id, *args, **kwargs):
		re_data = []
		reply_query = Answer.extend().where(Answer.parent_answer_id == int(answer_id))
		replies = await self.application.objects.execute(reply_query)
		count = 0
		for reply in replies:
			reply_dict = {
				"id":         reply.id,
				"user":       model_to_dict(reply.user),
				"content":    reply.content,
				"reply_user": model_to_dict(reply.reply_user),
				"reply_nums": reply.reply_nums,
				"add_time":   reply.add_time.strftime("%Y-%m-%d"),
			}
			count += 1
			re_data.append(reply_dict)
		if count == 0:
			self.set_status(404)

		self.finish(json.dumps(re_data))

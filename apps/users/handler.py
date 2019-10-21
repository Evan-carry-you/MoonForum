import json
from random import choice
from datetime import datetime

from tornado.web import RequestHandler
from apps.users.forms import SMSCodeForm, RegisterForm, LoginForm
from apps.users.models import User
import jwt

from MoonForum.settings import SMS_SETTING
from MoonForum.handler import RedisHandler
from apps.utils.AsyncSMS import JUHESMS

class LoginHandler(RedisHandler):
	async def post(self, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf8")
		param = json.loads(param)
		login_form = LoginForm.from_json(param)

		if login_form.validate():
			mobile = login_form.mobile.data
			password = login_form.password.data

			try:
				user = await self.application.objects.get(User, mobile=mobile)
				if not user.password.check_password(password):
					self.set_status(400)
					re_data['mobile'] = "用户名或密码错误"
				else:
					play_load = {
						"id":user.id,
						"nick_name":user.nick_name,
						"exp":datetime.utcnow()
					}
					token = jwt.encode(play_load, self.settings['jwt']['secret_key'], algorithm="HS256")
					re_data['id'] = user.id
					if user.nick_name is None:
						re_data['nick_name'] = user.mobile
					else:
						re_data['nick_name'] = user.nick_name
					re_data['token'] = token.decode("utf8")
			except User.DoesNotExist as e:
				self.set_status(400)
				re_data['mobile'] = "用户名不存在"
		else:
			pass
		self.finish(re_data)

class RegisterHandler(RedisHandler):
	async def post(self, *args, **kwargs):
		re_data = {}

		param = self.request.body.decode("utf-8")
		param = json.loads(param)
		register_form = RegisterForm.from_json(param)
		if register_form.validate():
			mobile = register_form.mobile.data
			code = register_form.code.data
			password = register_form.password.data

			if not self.redis_conn.get("{mobile}_{code}".format(mobile=mobile, code=code)):
				self.set_status(400)
				re_data['code'] = "验证码错误或者失效"
			else:
				try:
					exist_user = await self.application.objects.get(User, mobile=mobile)
					self.set_status(400)
					re_data['mobile'] = "用户已存在"
				except User.DoesNotExist as e:
					user = await self.application.objects.create(User, mobile=mobile, password=password)
					re_data['id'] = user.id
		else:
			for field in register_form.errors:
				re_data[field] = register_form.errors[field][0]
		print(re_data)
		self.finish(re_data)



class SMSHandler(RedisHandler):
	def generate_code(self):
		seeds = "1234567890"
		random_str = [choice(seeds) for _ in range(4)]
		return "".join(random_str)

	async def post(self, *args, **kwargs):
		re_data = {}
		param = self.request.body.decode("utf-8")
		param = json.loads(param)
		sms_form = SMSCodeForm.from_json(param)
		code = self.generate_code()

		if sms_form.validate():
			mobile = sms_form.mobile.data
			print(mobile)
			juhe = JUHESMS(**SMS_SETTING)
			re_json = await juhe.send_verify_code(mobile, code)
			if re_json['error_code'] != 0:
				self.set_status(400)
				re_data['msg'] = re_json['reason']
			else:
				# 将 code 写入到 redis 中
				self.redis_conn.set('{}_{}'.format(mobile, code), 1, 5 * 60)
		else:
			self.set_status(400)
			for field in sms_form.errors:
				re_data[field] = sms_form.errors[field][0]
		self.finish(re_data)

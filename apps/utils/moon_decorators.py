import functools

import jwt

from apps.users.models import User

def authenticated_async(method):
	@functools.wraps(method)
	async def wrapper(self, *args, **kwargs):
		tsessionid = self.request.headers.get('tsessionid', None)
		if tsessionid:
			try:
				send_data = jwt.decode(tsessionid,
				                       self.settings['jwt']['secret_key'],
				                       leeway=self.settings['jwt']['expire_time'], algorithms=['HS256'],
				                       options={"verify_exp":True})
				user_id = send_data['id']
				try:
					user = await self.application.objects.get(User, id = user_id)
					self._current_user = user
					await method(self, *args, **kwargs)
				except User.DoesNotExist as e:
					self.set_status(401)
			except jwt.ExpiredSignature:
				self.set_status(401)
		else:
			self.set_status(401)
	return wrapper
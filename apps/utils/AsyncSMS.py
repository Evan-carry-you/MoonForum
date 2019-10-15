from urllib.parse import urlencode

from tornado import httpclient
from tornado.httpclient import HTTPRequest
from tornado.ioloop import IOLoop
import json

from MoonForum.settings import SMS_SETTING


class JUHESMS():
	def __init__(self, *args, **kwargs):
		self.api_address = kwargs['api_address']
		self.key = kwargs['key']
		self.tpl_ids = kwargs['tpl_ids']

	async def send_verify_code(self, mobile, tpl_value):
		tpl_value = self.render_tpl_value("code", tpl_value)

		http_client = httpclient.AsyncHTTPClient()
		request = HTTPRequest(url=self.api_address, method="POST", body=urlencode({
			"key": self.key,
			"mobile": mobile,
			"tpl_id": self.tpl_ids['code'],
			"tpl_value": tpl_value
		}))

		res = await http_client.fetch(request)

		return json.loads(res.body.decode('utf-8'))

	@classmethod
	def render_tpl_value(cls, tpl_key, tpl_value):
		return "#{}#={}".format(tpl_key, tpl_value)


if __name__ == "__main__":
	sms = JUHESMS(**SMS_SETTING)
	from functools import partial

	send_sms = partial(sms.send_verify_code, "1888888888", "12345")
	loop = IOLoop.current()
	loop.run_sync(send_sms)

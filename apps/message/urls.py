from tornado.web import url

from apps.message.handler import *

url_pattern = [
	url(r"/messages/", MessageHandler, name="message"),
]

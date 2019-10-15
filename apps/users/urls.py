from tornado.web import url
from apps.users.handler import SMSHandler, RegisterHandler

url_pattern = [
	url("/code/", SMSHandler, name="SMSCode"),
	url("/register/", RegisterHandler, name="Register")
]
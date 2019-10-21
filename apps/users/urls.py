from tornado.web import url
from apps.users.handler import SMSHandler, RegisterHandler, LoginHandler

url_pattern = [
	url("/code/", SMSHandler, name="SMSCode"),
	url("/register/", RegisterHandler, name="Register"),
	url("/login/", LoginHandler, name="LoginHandler"),
]
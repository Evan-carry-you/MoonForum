from tornado.web import url
from apps.users.handler import SMSHandler, RegisterHandler, LoginHandler, ProfileHandler, HeadImagesHandler, PasswordHandler

url_pattern = [
	url("/code/", SMSHandler, name="SMSCode"),
	url("/register/", RegisterHandler, name="Register"),
	url("/login/", LoginHandler, name="LoginHandler"),
	url("/info/", ProfileHandler, name="ProfileHandler"),
	url("/headimages/", HeadImagesHandler, name="HeadImage"),
	url("/password/", PasswordHandler, name="PasswordHandler")
]
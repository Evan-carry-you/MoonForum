from tornado.web import url

from apps.community.handler import GroupHandler


url_pattern = [
	url("/groups/", GroupHandler, name="Group")
]

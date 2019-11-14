from tornado.web import url, StaticFileHandler

from apps.users import urls as user_urls
from apps.community import urls as community_urls
from apps.ueditor import urls as ueditor_urls
from apps.question import urls as question_urls
from apps.message import urls as message_urls
from MoonForum.settings import settings

url_pattern = [
	url("/{}/(.*)".format("media"), StaticFileHandler, {"path": settings['MEDIA_ROOT']})
]
url_pattern += user_urls.url_pattern
url_pattern += community_urls.url_pattern
url_pattern += ueditor_urls.url_pattern
url_pattern += question_urls.url_pattern
url_pattern += message_urls.url_pattern

# urls = [
# 	URLSpec('/', MainHandler, name="index")
# ]

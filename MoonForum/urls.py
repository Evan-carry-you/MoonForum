from tornado.web import url, StaticFileHandler

from apps.users import urls as user_urls
from apps.community import urls as community_urls
from MoonForum.settings import settings

url_pattern = [
	url("/{}/(.*)".format("media"), StaticFileHandler, {"path":settings['MEDIA_ROOT']})
]
url_pattern += user_urls.url_pattern
url_pattern += community_urls.url_pattern

# urls = [
# 	URLSpec('/', MainHandler, name="index")
# ]

from tornado.web import RequestHandler
import redis

class RedisHandler(RequestHandler):
	def __init__(self, application, request, **kwargs):
		super().__init__( application, request, **kwargs)
		self.redis_conn = redis.StrictRedis(**self.settings['redis'] )
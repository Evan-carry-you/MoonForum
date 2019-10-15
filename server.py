import os

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.options import define, options
from peewee_async import Manager

from MoonForum.settings import root, settings, database
from MoonForum.urls import url_pattern


options.define("port", 8888, help="Listening Port", type=int)

options.parse_command_line()
print(root)
options.parse_config_file(os.path.join(root, "cfg.conf"))

app = Application(
	url_pattern,
	**settings
)
#
if __name__ == "__main__":
	import wtforms_json
	wtforms_json.init()

	objects = Manager(database=database)
	database.set_allow_sync(False)
	app.objects = objects

	app.listen(options.port)
	print("Successful run on the port:{}".format(options.port))
	IOLoop.current().start()

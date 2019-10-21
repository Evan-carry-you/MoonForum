from datetime import datetime, date

def json_serial(object):
	if isinstance(object,(datetime,date)):
		return object.isoformat()
	raise TypeError("Type {} not serializable".format(type(object)))

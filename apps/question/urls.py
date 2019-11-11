from tornado.web import url

from apps.question.handler import QuestionHandler, QuestionDetailHandler, AnswerHandler, ReplyHandler

url_pattern = [
	url(r"/questions/", QuestionHandler, name="question_list"),
	url(r"/questions/([0-9]*)/", QuestionDetailHandler, name="question"),
	url(r"/questions/([0-9]*)/answers/", AnswerHandler, name="answer"),
	url(r"/answers/([0-9]*)/replys/", ReplyHandler, name="reply"),
]
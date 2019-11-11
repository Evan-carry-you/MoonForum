from tornado.web import url

from apps.community.handler import GroupHandler, GroupMemberHandler, GroupDetailHandler, PostHandler, PostDetailHandler, PostCommentHandler, CommentReplyHandler, CommentLikeHandler


url_pattern = [
	url("/groups/", GroupHandler, name="Group"),
	url("/groups/([0-9]*)/members/", GroupMemberHandler, name="GroupMember"),
	url("/groups/([0-9]*)/", GroupDetailHandler, name="GroupDetail"),
	url("/groups/([0-9]*)/posts/",PostHandler),
	url("/posts/([0-9]*)/", PostDetailHandler),
	url("/posts/([0-9]*)/comments/", PostCommentHandler),
	url("/comments/([0-9]*)/replys/", CommentReplyHandler),
	url("/comments/([0-9]*)/likes/", CommentLikeHandler)
]

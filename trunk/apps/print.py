# print.py

from biz.app import Application
from biz.content import TextContent


class Print(Application):
	def static(self):
		msg = self.options.get("print.message", "Hello, Biz!")
		self.content = TextContent(msg)


def load(environ, start_response, options):
	return Print(environ, start_response, options)


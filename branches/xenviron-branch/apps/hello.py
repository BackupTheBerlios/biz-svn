
from biz.app import Application
from biz.content import TextContent


class Hello(Application):
	def static(self):
		self.content = TextContent("Hello, World!")


def load(xenviron):
	return Hello(xenviron)


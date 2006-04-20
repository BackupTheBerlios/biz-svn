
from biz.app import Application
from biz.content import TextContent


class Wello(Application):
	def static(self):
		self.content = TextContent("Zello, World!")


def load(environ, start_response):
	return Wello(environ, start_response)


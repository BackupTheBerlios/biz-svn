
from biz.app import Application
from biz.content import TextContent


class SumApp(Application):
	def run(self):
		s = sum([float(p) for p in self.environ["biz.path"][1:]])
		self.content = TextContent(s)


def load(environ, start_response):
	return SumApp(environ, start_response)


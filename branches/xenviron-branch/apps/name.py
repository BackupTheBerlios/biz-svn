
from biz.app import Application
from biz.content import TextContent, HtmlContent


class Name(Application):
	def run(self):
		params = self.environ["biz.params"]

		try:
			page = "Your name is: <b>%(name)s %(surname)s</b>. It's a nice name!" % params
			self.content = HtmlContent(page)
		except KeyError:
			self.content = TextContent("Invalid request")


def load(environ, start_response):
	return Name(environ, start_response)



import biz


class Hello(biz.Application):
	def static(self):
		self.content = biz.TextContent("Hello, World!")


def load(xenviron):
	return Hello(xenviron)


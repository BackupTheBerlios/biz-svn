
#from biz.app import Application
#from biz.content import TextContent

import biz


class Hello(biz.Application):
	def static(self):
		self.content = biz.TextContent("Hello, World!")


def load(xenviron):
	return Hello(xenviron)


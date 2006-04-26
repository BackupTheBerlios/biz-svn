# app.py -- Biz application

from biz.response import Response
from utility import Struct, Heads

from content import TextContent


class Application:
	def __init__(self, xenviron):
		self.options = xenviron.options
		self.content = TextContent("application default")
		self.code = 200
		self.heads = Heads()

		self.refresh(xenviron)
		self.static()

	def refresh(self, xenviron):
		"""prepare the application to run

		* Extend this method, if you require custom preparation
		"""
		self.path = xenviron.path
		self.params = xenviron.params
		self.session = xenviron.session
		self.cookies = xenviron.cookies

	def static(self):
		"""prepare static content

		* Override this method to prepare content that will be prepared once
		"""
		pass

	def run(self):
		"""execute the application

		* Override this method for dynamic/semi-dynamic content
		* You should supply self.content here with your content,
		* Optionally you may supply self.rcode and/or
		self.rheads
		"""
		pass

	def get(self):
		xenviron = Struct()  # FUTURE
		xenviron.cookies = self.cookies
		xenviron.session = self.session
		return (xenviron,Response(self.code, self.content, **self.heads._getdict()))


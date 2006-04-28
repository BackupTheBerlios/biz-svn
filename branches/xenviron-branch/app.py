# app.py -- Biz application

from biz.response import Response
from utility import Struct, Heads

from content import TextContent, EmptyContent


class Application:
	def __init__(self, xenviron):
		self.options = xenviron.options
		self.content = TextContent("application default")

		self.refresh(xenviron)
		self.static()

	def refresh(self, xenviron):
		"""prepare the application to run

		* Extend this method, if you require custom preparation
		"""
		self.args = xenviron.args
		self.kwargs = xenviron.kwargs
		self.session = xenviron.session
		self.cookies = xenviron.cookies

		self.code = 200
		self.heads = Heads()

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

	def redirect(self, location):
		self.code = 307
		self.heads.location = location
		self.content = EmptyContent()


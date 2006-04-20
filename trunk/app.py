# app.py -- Biz application

from biz.response import Response


class Application:
	def __init__(self, environ, start_response):
		##self.environ = environ
		##self.start_response = start_response
		##self.response = Response(start_response, content=None)
		self.rcode = 200
		self.content = None
		self.rheads = None

		self.refresh(environ, start_response)		
		self.static()

	def refresh(self, environ, start_response):
		"""prepare the application to run

		* Extend this method, if you require custom preparation
		"""
		self.environ = environ
		self.response = Response(start_response, content=None)
		##self.rcode = 200
		##self.content = None
		##self.rheads = None

		##self.run()

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

	def get_response(self):
		r = self.response
		r.content = self.content
		r.rcode = self.rcode
		if self.rheads:
			r.heads = self.rheads

		return r.get_response()


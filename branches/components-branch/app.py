# app.py -- Biz application

##from biz.response import Response
from biz.component import Component


class Application(Component):
	requires = ["biz.environ", "biz.startresponse",
				"biz.env.path", "biz.env.params"]
	accepts = ["biz.app.options"]
	provides = ["biz.environ",   ## "biz.startresponse",
				"biz.response.code", "biz.response.content",
				"biz.response.heads"]

	def __init__(self, resources=None):
		Component.__init__(self)

		self.rcode = 200
		self.content = None
		self.rheads = {}

		self.refresh()
		self.static()


	def refresh(self):
		"""prepare the application to run

		* Extend this method, if you require custom preparation
		"""
		##self.environ = environ
		##self.response = Response(start_response, content=None)
		self.collect()
		self.environ = self.properties["biz.environ"]  ## ?
		self.path = self.properties["biz.env.path"]
		self.params = self.properties["biz.env.params"]
		self.options = self.properties.get("biz.app.options", {})
		##self.response = Response()
		##self.provideto(self.response)
		##self.response.new()

	def static(self):
		"""prepare static content

		* Override this method to prepare content that will not change
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

	def prepare(self):
		Component.prepare(self)

		self.refresh()
		self.run()

		self.providing["biz.environ"] = self.properties["biz.environ"]
		##self.providing["biz.startresponse"] = self.properties["biz.startresponse"]

		self.providing["biz.response.content"] = self.content
		self.rheads["content-length"] = self.content._clen
		self.rheads["content-type"] = self.content.ctype
		self.providing["biz.response.heads"] = self.rheads
		self.providing["biz.response.code"] = self.rcode

		assert self.providesall(), "This component cannot provide all"



	##def get_response(self):
	##    r = self.response
	##    r.content = self.content
	##    r.rcode = self.rcode
	##    if self.rheads:
	##        r.heads = self.rheads
	##
	##    return r.get_response()


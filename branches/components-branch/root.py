# root.py -- Root application


import imp
import time
import os
import os.path
from ConfigParser import ConfigParser, NoOptionError

from biz.component import Component
from biz.response import Response, RESPONSES
from biz.content import TextContent


APP_OPTION_PREFIX = "biz.app."

class ApplicationInfo(object):
	__slots__ = "name","mpath","cpath","body","mtime","ctime","usage","hotplug","options","class_"

	def __init__(self, name, mpath=None, cpath=None, class_=None, body=None,
			mtime=0, ctime=0, options=None, hotplug=False):
		self.name = name
		self.mpath = mpath
		self.cpath = cpath
		self.class_ = class_
		self.body = body
		self.mtime = mtime  # module modification time
		self.ctime = ctime  # configuration modification time
		self.usage = 0
		self.hotplug = hotplug
		self.options = options or {}

	known_options = ["path", "hotplug", "class"]

	def _reload_options(self):
		self.ctime = os.stat(self.cpath).st_mtime
		cfg = ConfigParser()
		cfg.read(self.cpath)

		sections = cfg.sections()

		assert len(sections) > 0, \
				"%s should have at least one section" % self.path

		options = dict(cfg.items(sections[0]))

		assert options.has_key("class") ^ options.has_key("path"), \
			"class OR path should be in options"

		self.hotplug = options.get("hotplug", False)
		self.class_ = options.get("class", None)
		self.mpath = options.get("path", "")

		return dict([(k,v) for k,v in options.iteritems() if k not in self.known_options])

	def _reload(self, root):
		root.providing["biz.app.options"] = self._reload_options()

		if self.class_:
			m = __import__(self.class_, None, None, ["load"])
			self.body = m.load(root)

		else:
			self.mtime = os.stat(self.mpath).st_mtime			
			path, modname = os.path.split(self.mpath)
			modname = modname.split(".py")[0]
			self.body = imp.load_module(modname, \
				*imp.find_module(modname, [path])).load(root)

	def unload(self):
		self.body = None

	def _is_modified(self):
		if not self.hotplug:
			return False

		ctime = os.stat(self.cpath).st_mtime
		if ctime > self.ctime:
			return True

		if self.class_:
			return False

		mtime = os.stat(self.mpath).st_time
		if mtime > self.mtime:
			return True

		return False

	def __call__(self, root):
		if not self.body or self._is_modified():
			self._reload(root)

		return self
		

class Root(Component):
	requires = []
	accepts = ["biz.response.code", "biz.response.content",
				"biz.response.heads"]
	provides = ["biz.environ", "biz.startresponse",
				"biz.env.path", "biz.env.params",
				"biz.debug.app.usage", "biz.error.code",
				"biz.error.message", "biz.app.options"]

	def __init__(self):
		Component.__init__(self)

##		self._apps = {}  # cached apps
		self._applist = {}  # all apps
		self._index = None  # index app
		self._error = None
		##self.environ = None
		##self.start_response = None
		self.providing["biz.environ"] = None
		self.providing["biz.startresponse"] = None

	def register_app(self, name, cpath):
		if name not in self._applist:
			self._applist[name] = ApplicationInfo(name, cpath=cpath)

	def register_index(self, name, cpath):
		self._index = ApplicationInfo(name, cpath=cpath)

	def register_error(self, name, cpath):
		self._error = ApplicationInfo(name, cpath=cpath)

	def _default_index(self):
		page = "Index method is left out."

		self.properties["biz.response.code"] = 200
		self.properties["biz.response.content"] = TextContent(page)

		return self.return_response()

	def _default_error(self):
		self.properties["biz.response.code"] = self.providing["biz.error.code"]
		self.properties["biz.response.content"] = TextContent(self.providing["biz.error.message"])
		return self.return_response()
		##code = self.environ["biz.error.code"]
		##msg = self.environ["biz.error.message"]
		##
		##self.start_response("%s error" % code, [("content-type","text/plain")])
		##return msg

	def __call__(self, environ, start_response):
		def tuplize(x):
			l = x.split("=")[:2]
			if len(l) == 1:
				l.append(True)
			return tuple(l)

		##self.environ = environ
		##self.start_response = start_response

		path = [p for p in environ["PATH_INFO"].split("/") if p] or [""]
		if "QUERY_STRING" in environ:
			params = dict([tuplize(x) for x in environ["QUERY_STRING"].split("&") if x])
		else:
			params = {}

		self.providing["biz.environ"] = environ
		self.providing["biz.startresponse"] = start_response
		self.providing["biz.env.path"] = path
		self.providing["biz.env.params"] = params

		##environ["biz.path"] = path
		##environ["biz.params"] = params

		if not path[0]:
			if not self._index:
				return self._default_index()

			##app = self._index(environ, start_response)
			app = self._index(self)
		else:
			try:
				name = path[0]
				##app = self._applist[name](environ, start_response)
				app = self._applist[name](self)
			except KeyError:
				self.providing["biz.error.code"] = 404
				self.providing["biz.error.message"] = "Method not found."

				if self._error:
					app = self._error(self)
				else:
					return self._default_error()					

		app.usage += 1
		self.providing["biz.debug.app.usage"] = str(app.usage)

		self.collectfrom(app.body)
		return self.return_response()

	def return_response(self):
		start_response = self.providing["biz.startresponse"]

		rcode = self.properties.get("biz.response.code", 400)
		content = self.properties.get("biz.response.content", 
				TextContent("application error"))
		rheads = self.properties.get("biz.response.heads", {})
		##rheads["content-length"] = str(content._clen)
		##rheads["content-type"] = content.ctype

		return Response(start_response, rcode, content, rheads).get_response()

		##start_response("%d %s" % \
		##        (rcode,RESPONSES.get(rcode, ["Unknown"])[0]),
		##        [x for x in rheads.iteritems()])		
		##
		##return content.get_content()

	def configure(self, cfgfilename, update=False):
		cfg = ConfigParser()
		cfg.read(cfgfilename)

		apps = "applications"

		assert cfg.has_section(apps), \
			"Root configuration file should have `applications` section"

		for app, cpath in cfg.items(apps):
			if not app in self._applist:
				self.register_app(app, cpath)

		index = "index"
		if cfg.has_section(index):
			app,cpath = cfg.items(index)[0]
			self.register_index(app, cpath)

		error = "error"
		if cfg.has_section(error):
			app,cpath = cfg.items(error)[0]
			self.register_error(app, cpath)






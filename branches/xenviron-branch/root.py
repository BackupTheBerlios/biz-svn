# root.py -- Root application


import imp
import time
import os
import os.path
from ConfigParser import ConfigParser, NoOptionError


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

		self.options = options

	def _reload(self, environ, start_response):
		self._reload_options()

		if self.class_:
			m = __import__(self.class_, None, None, ["load"])
			self.body = m.load(environ, start_response, self.options)

		else:
			self.mtime = os.stat(self.mpath).st_mtime			
			path, modname = os.path.split(self.mpath)
			modname = modname.split(".py")[0]
			self.body = imp.load_module(modname, \
				*imp.find_module(modname, [path])).load(environ, \
						start_response, self.options)

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

	def __call__(self, environ, start_response):
		if not self.body or self._is_modified():
			self._reload(environ, start_response)

		return self
		

class BizRoot:
	def __init__(self):
##		self._apps = {}  # cached apps
		self._applist = {}  # all apps
		self._index = None  # index app
		self._error = None
		self.environ = None
		self.start_response = None

	def register_app(self, name, cpath):
		if name not in self._applist:
			self._applist[name] = ApplicationInfo(name, cpath=cpath)

	def register_index(self, name, cpath):
		self._index = ApplicationInfo(name, cpath=cpath)

	def register_error(self, name, cpath):
		self._error = ApplicationInfo(name, cpath=cpath)

	def _default_index(self):
		try:
			try:
				f = file("doc/welcome.html")
				page = f.read()
			finally:
				f.close()

		except IOError:
			page = "Index method is left out."

		self.start_response("200 Index", [("content-type","text/html")])
		return page

	def _default_error(self):
		code = self.environ["biz.error.code"]
		msg = self.environ["biz.error.message"]

		self.start_response("%s error" % code, [("content-type","text/plain")])
		return msg

	def __call__(self, environ, start_response):
		def tuplize(x):
			l = x.split("=")[:2]
			if len(l) == 1:
				l.append(True)
			return tuple(l)

		self.environ = environ
		self.start_response = start_response

		path = [p for p in environ["PATH_INFO"].split("/") if p] or [""]
		if "QUERY_STRING" in environ:
			params = dict([tuplize(x) for x in environ["QUERY_STRING"].split("&") if x])
		else:
			params = {}

		environ["biz.path"] = path
		environ["biz.params"] = params

		if not path[0]:
			if not self._index:
				return self._default_index()

			app = self._index(environ, start_response)
		else:
			try:
				name = path[0]
				app = self._applist[name](environ, start_response)
			except KeyError:
				environ["biz.error.code"] = "404"
				environ["biz.error.message"] = "Method not found."

				if self._error:
					app = self._error(environ, start_response)
				else:
					return self._default_error()					

		app.usage += 1
		environ["biz.debug.app.usage"] = str(app.usage)

		app.body.refresh(environ, start_response)
		app.body.run()
		return app.body.get_response()

	known_options = ["path", "hotplug", "class"]

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






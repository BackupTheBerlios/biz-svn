# root.py -- Root application


import imp
import time
import os
import os.path


class Application(object):
	__slots__ = "name","path","body","mtime","usage"

	def __init__(self, name, path, body, mtime=None):
		self.name = name
		self.path = path
		self.body = body
		self.mtime = mtime
		self.usage = 0


class Root:
	def __init__(self):
		self._apps = {}  # cached apps
		self._applist = {}  # all apps
		self._index = None  # index app
		self._error = None

	def register_app(self, name, path):
		if name not in self._applist:
			self._applist[name] = Application(name, path, None, os.stat(path).st_mtime)

	##def register_index(self, name, path):
	##    self._index = Application(name, path, self._load_body(name, path))
	##
	##def register_error(self, name, path):
	##    self._error = Application(name, path, self._load_body(name, path))

	##def _load_body(self, name, path):
	def _load_body(self, path):
		path, modname = os.path.split(path)
		modname = modname.split(".py")[0]
		##return imp.load_module(name, *imp.find_module(name, [path]))
		return imp.load_module(modname, *imp.find_module(modname, [path]))

	def _cache_app(self, name):
		app = self._applist[name]
		app.body = self._load_body(app.path)
		self._apps[name] = app

	def _uncache_app(self, name):
		app = self._apps[name]
		app.body = None
		del self._apps[name]

	def _default_index(self, environ, start_response):
		try:
			try:
				f = file("doc/welcome.html")
				page = f.read()
			finally:
				f.close()

		except IOError:
			page = "Index method is left out."

		start_response("200 Index", [("content-type","text/html")])
		return page

	def _default_error(self, environ, start_response):
		code = environ["biz.error.code"]
		msg = environ["biz.error.message"]

		start_response("%s error" % code, [("content-type","text/plain")])
		return msg

	def __call__(self, environ, start_response):
		def tuplize(x):
			l = x.split("=")[:2]
			if len(l) == 1:
				l.append(True)
			return tuple(l)

		path = [p for p in environ["PATH_INFO"].split("/") if p] or [""]
		if "QUERY_STRING" in environ:
			print "x"  ##
			params = dict([tuplize(x) for x in environ["QUERY_STRING"].split("&") if x])
		else:
			params = {}

		environ["biz.path"] = path
		environ["biz.params"] = params

		if not path[0]:
			if not self._index:
				return self._default_index(environ, start_response)

			app = self._index
			in_cache = 1

		else:
			try:
				name = path[0]
				app = self._apps[name]
				# check whether the application is modified
				mt = os.stat(app.path).st_mtime
				if not app.mtime or mt > app.mtime:
					app.body = self._load_body(app.path)
					
				in_cache = 1
			except KeyError:  # app is not cached
				try:
					self._cache_app(name)
					app = self._apps[name]
					in_cache = 0
				except KeyError:
					environ["biz.error.code"] = "404"
					environ["biz.error.message"] = "Method not found."

					if self._error:
						app = self._error
					else:
						return self._default_error(environ, start_response)					

		app.usage += 1
		environ["biz.application.debug.usage"] = str(app.usage)
		environ["biz.application.debug.in_cache"] = str(in_cache)

		return app.body.run(environ, start_response)


root = Root()
##root.register_app("hello", "apps")
root.register_app("sum", "apps/sum/__init__.py")
##root.register_app("file", "apps")
root.register_app("zello", "apps/wello.py")
##root.register_index("wello", "apps")
##root.register_app("bizpath", "apps")
##root.register_app("name", "apps")


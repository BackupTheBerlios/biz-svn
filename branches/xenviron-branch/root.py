# root.py -- Root application


import imp
import time
import os
import os.path
from ConfigParser import ConfigParser, NoOptionError
from Cookie import SimpleCookie
import urllib

from biz.utility import Struct
from biz.content import TextContent
from biz.response import Response
from biz.session import SessionManager, SessionError

__all__ = ["Root"]


class ApplicationInfo(object):
	__slots__ = ("name","mpath","cpath",
				"body","mtime","ctime",
				"usage","hotplug","class_")

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
		##self.options = options or {}

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

		##self.options = options
		return options

	def _reload(self, xenviron):
		xenviron.options = self._reload_options()

		if self.class_:
			m = __import__(self.class_, None, None, ["load"])
			self.body = m.load(xenviron)

		else:
			self.mtime = os.stat(self.mpath).st_mtime			
			path, modname = os.path.split(self.mpath)
			modname = modname.split(".py")[0]
			self.body = imp.load_module(modname, \
				*imp.find_module(modname, [path])).load(xenviron)

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

		mtime = os.stat(self.mpath).st_mtime
		if mtime > self.mtime:
			return True

		return False

	def __call__(self, xenviron):
		if not self.body or self._is_modified():
			self._reload(xenviron)

		return self
		

class Root:
	def __init__(self):
##		self._apps = {}  # cached apps
		self._applist = {}  # all apps
		self._index = None  # index app
		self._error = None
		self.environ = None
		self.start_response = None
		self.sessionman = SessionManager()

	def register_app(self, name, cpath):
		if name not in self._applist:
			self._applist[name] = ApplicationInfo(name, cpath=cpath)

	def register_index(self, name, cpath):
		self._index = ApplicationInfo(name, cpath=cpath)

	def register_error(self, name, cpath):
		self._error = ApplicationInfo(name, cpath=cpath)

	def _default_index(self):
		page = TextContent("Index method is left out.")
		return self._prepare_response(Response(200, page))
		
	def _default_error(self, code, message):
		page = TextContent(message)
		return self._prepare_response(Response(code, page))

	def __call__(self, environ, start_response):
		def tuplize(x):
			l = x.split("=")[:2]
			if len(l) == 1:
				l.append(True)
			return tuple(l)

		self.environ = environ
		self.start_response = start_response

		path_info = urllib.unquote_plus(environ["PATH_INFO"])

		path = [p for p in path_info.split("/") if p] or [""]
		if "QUERY_STRING" in environ:
			query_string = urllib.unquote_plus(environ["QUERY_STRING"])
			params = dict([tuplize(x) for x in query_string.split("&") if x])
		else:
			params = {}

		xenviron = Struct()
		xenviron.args = path
		xenviron.kwargs = params
		xenviron.cookies = SimpleCookie(environ.get("HTTP_COOKIE", ""))

		try:
			xenviron.cookies, xenviron.session = self.sessionman.get_session(xenviron.cookies)
		except SessionError:
			xenviron.session = self.sessionman.new_session()


		if not path[0]:
			if not self._index:
				return self._default_index()

			app = self._index(xenviron)
		else:
			try:
				name = path[0]
				app = self._applist[name](xenviron)
			except KeyError:
				##environ["biz.error.code"] = "404"
				##environ["biz.error.message"] = "Method not found."
				xenviron.error_code = 404
				xenviron.error_message = "Method not found"

				if self._error:
					app = self._error(xenviron)
				else:
					return self._default_error(xenviron.error_code, 
							xenviron.error_message)

		app.body.refresh(xenviron)
		app.body.run()
		app_xenviron, response = app.body.get()
		# further process the app_xenviron
		self.sessionman.update(app_xenviron.session)
		# return preparations
		cookies = SimpleCookie()
		cookies.update(app_xenviron.cookies)
		cookies.update(app_xenviron.session.sidcookie)
		##try:  # XXX
		cookies = str(cookies).split()[1]
		##except IndexError:
			##cookies = "sid=0"
		##response.heads.set_cookie = str(cookies)
		response.heads.set_cookie = cookies
		return self._prepare_response(response)

	def _prepare_response(self, response):
		rc, rh, ct = response.get_forwsgi()
		self.start_response(rc, rh)

		return ct

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





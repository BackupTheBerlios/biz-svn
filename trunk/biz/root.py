# root.py -- Root application
# Routes the applications

# Biz web application framework
# Copyright (C) 2006  Yuce Tekol
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


import imp
import time
import os
import os.path
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from Cookie import SimpleCookie
import urllib
from cgi import FieldStorage

from biz.app import Application
from biz.utility import Struct
from biz.content import TextContent
from biz.response import Response
from biz.session import SessionManager, SessionError
from biz.errors import *

__all__ = ["Root"]

## def _(s):  # TODO: Replace this with a true i18n function
## 	return s

import gettext
try:
	_ = gettext.translation("messages", "/home/yuce/prj/biz/biz/locale").ugettext # XXX
except:
	print _(u"Locale not found")
	_ = lambda s: s


class ApplicationInfo(object):
	__slots__ = ("name","mpath","cpath",
				"body","mtime","ctime",
				"usage","hotplug","module", "class_")

	def __init__(self, name, mpath=None, cpath=None, module=None, body=None,
			mtime=0, ctime=0, options=None, hotplug=False):
		self.name = name
		self.mpath = mpath
		self.cpath = cpath
		self.module = module
		self.body = body
		self.mtime = mtime  # module modification time
		self.ctime = ctime  # configuration modification time
		self.usage = 0
		self.hotplug = hotplug
		self.class_ = None  # Warning! this is not in the parameter list ^

	def _reload_options(self):
		try:
			self.ctime = os.stat(self.cpath).st_mtime
			cfg = ConfigParser()
			cfg.read(self.cpath)
		except OSError:
			raise ConfigFileNotFoundError(self.cpath, source="default config")

		sections = cfg.sections()

		if len(sections) < 1:
			raise ImproperConfigFileError(self.cpath,
					_(u"%s should have at least one section" % self.cpath))

		options = dict(cfg.items(sections[0]))

		if not(options.has_key("module") ^ options.has_key("path")):
			raise ImproperConfigFileError(self.cpath,
					_(u"%s should have a ``module`` or ``path`` option, but not both" % self.cpath))

		self.hotplug = options.get("hotplug", False)
		self.module = options.get("module", None)
		self.mpath = options.get("path", "")
		self.class_ = options.get("class", "")

		return options

	def _reload(self, xenviron):
		xenviron.options = self._reload_options()

		if self.module:
			if self.class_:
				try:
					m = __import__(self.module, None, None, [self.class_])
					self.body = m.__getattribute__(self.class_)(xenviron)
				except ImportError:
					raise ModuleNotFoundError(self.module, source=self.cpath)
				except AttributeError:
					raise ApplicationNotFoundInModuleError(self.class_,
							where=self.module, source=self.cpath)
			else:
				try:
					m = __import__(self.module, None, None, ["load"])
					self.body = m.load(xenviron)
				except ImportError:
					raise NoApplicationExistsError(self.module, source=self.cpath)

		else:
			self.mtime = os.stat(self.mpath).st_mtime
			path, modname = os.path.split(self.mpath)
			modname = modname.split(".py")[0]
			m = imp.load_module(modname, \
					*imp.find_module(modname, [path]))

			if self.class_:
				self.body = m.__getattribute__(self.class_)(xenviron)
			else:
				try:
					self.body = m.load(xenviron)
				except AttributeError:
					for v in m.__dict__.itervalues():
						if issubclass(v, Application):
							self.body = v(xenviron)
							break
					else:
						raise NoApplicationExistsError(path, source=self.cpath)

	def unload(self):
		self.body = None

	def _is_modified(self):
		if not self.hotplug:
			return False

		ctime = os.stat(self.cpath).st_mtime
		if ctime > self.ctime:
			return True

		if self.module:
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
		self._applist = {}  # all apps
		self._index = None  # index app
		self._error = None
		self.environ = None
		self.start_response = None
		self.sessionman = SessionManager()
		self.debug = False

	def register_app(self, name, cpath):
		if name not in self._applist:
			self._applist[name] = ApplicationInfo(name, cpath=cpath)

	def register_index(self, name, cpath):
		self._index = ApplicationInfo(name, cpath=cpath)

	def register_error(self, name, cpath):
		self._error = ApplicationInfo(name, cpath=cpath)

	def _default_index(self):
		page = TextContent(_(u"Index method is left out."))
		return self._prepare_response(Response(200, page))
		
	def _default_error(self, code, message):
		page = TextContent(message)
		return self._prepare_response(Response(code, page))

	def __call__(self, environ, start_response):
		return self.run(environ, start_response)

	def run(self, environ, start_response):
		def tuplize(x):
			l = x.split("=")[:2]
			if len(l) == 1:
				l.append(True)
			return tuple(l)

		self.environ = environ
		self.start_response = start_response

		try:	
			path_info = urllib.unquote_plus(environ["PATH_INFO"])
		except KeyError:
			raise WSGIKeyNotPresentError("PATH_INFO")

		path = [p for p in path_info.split("/") if p] or [""]
		if "QUERY_STRING" in environ:
			query_string = urllib.unquote_plus(environ["QUERY_STRING"])
			params = dict([tuplize(x) for x in query_string.split("&") if x])
		else:
			params = {}

		# a dirty little trick to deny FieldStorage to use QUERY_STRING
		self.environ["QUERY_STRING"] = ""

		xenviron = Struct()
		xenviron.args = path
		xenviron.kwargs = params
		try:
			xenviron.fields = FieldStorage(environ=self.environ,
					fp=self.environ["wsgi.input"])
		except KeyError:
			raise WSGIKeyNotPresentError("wsgi.input")
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
				xenviron.error_code = 404
				xenviron.error_message = _(u"Method not found")

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
		cookies = str(cookies).split()[1]
		response.heads.set_cookie = cookies
		return self._prepare_response(response)

	def _prepare_response(self, response):
		rc, rh, ct = response.get_forwsgi()
		self.start_response(rc, rh)

		return ct

	@staticmethod
	def configure(cfgfilename, update=False):
		root = Root()
		cfg = ConfigParser()
		cfg.read(cfgfilename)

		apps = "applications"

		for app, cpath in cfg.items(apps):
			if not app in root._applist:
				root.register_app(app, cpath)

		index = "index"
		if cfg.has_section(index):
			app,cpath = cfg.items(index)[0]
			root.register_index(app, cpath)

		error = "error"
		if cfg.has_section(error):
			app,cpath = cfg.items(error)[0]
			root.register_error(app, cpath)

		try:
			timeout = cfg.getint("root", "timeout")
		except (NoSectionError,NoOptionError):
			timeout = 0

		root.sessionman.timeout = timeout

		try:
			expiretime = cfg.getint("root", "expiretime")
		except (NoSectionError,NoOptionError):
			expiretime = 0

		root.sessionman.expiretime = expiretime

		try:
			debug = cfg.getboolean("root", "debug")
		except (NoSectionError,NoOptionError):
			debug = False

		root.debug = debug

		return root


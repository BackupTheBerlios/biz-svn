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
import threading

from biz.app import Application
from biz.utility import Struct, Heads
from biz.content import TextContent
from biz.response import Response
from biz.session import SessionManager, SessionError
from biz.errors import *

__all__ = ["Root"]

sessionman_lock = threading.Lock()
applist_lock = threading.Lock()

import gettext
## try:
## 	_ = gettext.translation("messages", "/home/yuce/prj/biz/biz/locale").ugettext # XXX
## except:
## 	print _(u"Locale not found")

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
				except ImportError, e:
					print "Import error:", e
				try:
					self.body = m.load(xenviron)
## 				except (ImportError,AttributeError):
				except AttributeError, e:
					print "Attr error:", e
## 					raise NoApplicationExistsError(self.module, source=self.cpath)

		else:
			self.mtime = os.stat(self.mpath).st_mtime
			path, modname = os.path.split(self.mpath)
			modname = modname.split(".py")[0]
			m = imp.load_module(modname, \
					*imp.find_module(modname, [path]))

			if self.class_:
				try:
					self.body = m.__getattribute__(self.class_)(xenviron)
				except AttributeError, e:
					raise ApplicationNotFoundInModuleError(self.class_,
						where=self.mpath, source="root", msg=e)
			else:
				try:
					self.body = m.load(xenviron)
				except AttributeError:
##					for v in m.__dict__.itervalues():
## 						try:
## 							if issubclass(v, Application):
## 								self.body = v(xenviron)
## 								break
## 						except TypeError:
## 							pass
## 					else:
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
			try:
				applist_lock.acquire()
				self._reload(xenviron)
			finally:
				applist_lock.release()

		return self
		

class Root:
	def __init__(self, meltscriptname=False):
		self._applist = {}  # all apps
		self._index = None  # index app
		self._error = None
		self.environ = None
		self.start_response = None
		self.sessionman = SessionManager()
		self.debug = False
		self.meltscriptname = meltscriptname

	def register_app(self, name, cpath):
		if name not in self._applist:
			self._applist[name] = ApplicationInfo(name, cpath=cpath)

	def register_index(self, name, cpath):
		self._index = ApplicationInfo(name, cpath=cpath)

	def register_error(self, name, cpath):
		self._error = ApplicationInfo(name, cpath=cpath)

	def _default_index(self, start_response):
		response = Struct()
		response.content = TextContent(_(u"Index method is left out"))
		response.code = 404
		response.heads = Heads()
		return self._prepare_response(start_response, Response(response))
		
	def _default_error(self, start_response, code, message):
		response = Struct()
		response.content = TextContent(message)
		response.code = code
		response.heads = Heads()
		return self._prepare_response(start_response, Response(response))

	def __call__(self, environ, start_response):
		return self.run(environ, start_response)

	def run(self, environ, start_response):
		def tuplize(x):
			l = x.split("=")[:2]
			if len(l) == 1:
				l.append(True)
			return tuple(l)

		try:	
			path_info = urllib.unquote_plus(environ["PATH_INFO"])
		except KeyError:
			path_info = ""
		
		if not self.meltscriptname:
			try:
				path_info = "%s%s" %(environ["SCRIPT_NAME"],path_info)
			except KeyError:
				raise WSGIKeyNotFoundError("SCRIPT_NAME", source="root.py")
			
		xenviron = Struct()
		xenviron.path = Struct()
		xenviron.path.endswithslash = path_info.endswith("/")			
			
		path = [p for p in path_info.split("/") if p] or [""]
		if "QUERY_STRING" in environ:
			query_string = urllib.unquote_plus(environ["QUERY_STRING"])
			params = dict([tuplize(x) for x in query_string.split("&") if x])
		else:
			params = {}

		# a dirty little trick to deny FieldStorage to use QUERY_STRING
		environ["QUERY_STRING"] = ""

		if self.meltscriptname:
			try:
				xenviron.path.args = path
				xenviron.path.scriptname = environ["SCRIPT_NAME"]
			except KeyError:
				raise WSGIKeyNotPresentError("SCRIPT_NAME")
		else:
			xenviron.path.args = path
			xenviron.path.scriptname = ""
		
		xenviron.path.kwargs = params
		try:
			xenviron.fields = FieldStorage(environ=environ,
						fp=environ["wsgi.input"])
		except KeyError:
			raise WSGIKeyNotPresentError("wsgi.input")
			
		xenviron.cookies = SimpleCookie(environ.get("HTTP_COOKIE", ""))

		try:
			sessionman_lock.acquire()
			try:
				xenviron.cookies, xenviron.session = self.sessionman.get_session(xenviron.cookies)
			except SessionError:
				xenviron.session = self.sessionman.new_session()
		finally:
			sessionman_lock.release()
			
		appname = path[0]

		if not appname:
			if not self._index:
				return self._default_index(start_response)

			app = self._index(xenviron)
		else:
			try:
				name = appname
				app = self._applist[name](xenviron)
				
			except KeyError:
				xenviron.error_code = 404
				xenviron.error_message = _(u"Method not found")

				if self._error:
					app = self._error(xenviron)
				else:
					return self._default_error(start_response, xenviron.error_code, 
							xenviron.error_message)
							
		response = app.body(xenviron)
		
		try:
			sessionman_lock.acquire()
			# further process the app_xenviron
			self.sessionman.update(response.session)
		finally:
			sessionman_lock.release()

		return self._prepare_response(start_response, Response(response))

	def _prepare_response(self, start_response, response):
		rc, rh, ct = response.get_forwsgi()
		start_response(rc, rh)

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


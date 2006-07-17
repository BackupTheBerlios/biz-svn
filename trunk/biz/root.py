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
import threading

from biz.app import Application
from biz.utility import Struct, Heads, CookieJar, BizFieldStorage
from biz.content import TextContent
from biz.response import Response
from biz.session import SessionManager, SessionError
from biz.errors import *

__all__ = ["Root"]

sessionman_lock = threading.Lock()
applist_lock = threading.Lock()

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
		self.usage = 0  # XXX: Not used at the moment
		self.hotplug = hotplug
		self.class_ = None  # Warning! this is not in the parameter list ^

	def _reload_options(self):
		try:
			self.ctime = os.stat(self.cpath).st_mtime
			cfg = ConfigParser()
			cfg.readfp(file(self.cpath))
		except OSError, e:
			raise ConfigFileNotFoundError(self.cpath, msg=e, source=__file__)
		except IOError, e:
			raise ConfigFileNotFoundError(self.cpath, msg=e, source=__file__)

		sections = cfg.sections()

		if len(sections) < 1:
			raise ImproperConfigFileError(self.cpath,
					_(u"%s should have at least one section" % self.cpath))
					
		options = Struct()
		try:
			options.main = mainsect = dict(cfg.items("main"))
		except NoSectionError:
			raise ImproperConfigFileError(self.cpath, source="root")
			
		options.sections = sections
		options.sections.remove("main")  # This is removed, so app won't get this twice
		
		# module and path options are mutually exclusive
		if not(mainsect.has_key("module") ^ mainsect.has_key("path")):
			raise ImproperConfigFileError(self.cpath,
					_(u"%s should have a ``module`` or ``path`` option, but not both" % self.cpath))

		# pass the remaining sections to the app, so it may use them
		for sectname in sections:
			options[sectname] = dict(cfg.items(sectname))

		self.hotplug = mainsect.get("hotplug", False)
		self.module = mainsect.get("module", None)
		self.mpath = mainsect.get("path", "")
		self.class_ = mainsect.get("class", "")

		return options

	def _reload(self, xenviron):
		xenviron.options = self._reload_options()

		# app is standard
		if self.module:
			# class of the app is given
			if self.class_:
				try:
					m = __import__(self.module, None, None, [self.class_])
				except ImportError, e:
					raise ModuleNotFoundError(self.module, msg=e, source=self.cpath)
					
				try:
					# create the application
					self.body = m.__getattribute__(self.class_)(xenviron)
				except AttributeError, e:
					# XXX: this is also raised on AttributeError in app's constructor
					raise ApplicationNotFoundInModuleError(self.class_, msg=e,
							where=self.module, source=self.cpath)
			else:
				# a load function should be present in the module
				try:
					m = __import__(self.module, None, None, ["load"])
				except ImportError, e:
					raise ModuleNotFoundError(self.module, msg=e, source=self.cpath)
					
				try:
					self.body = m.load(xenviron)
				except AttributeError, e:
					# XXX: this is also raised on AttributeError in app's constructor
					raise NoApplicationExistsError(self.module, msg=e, source=self.cpath)

		else:
			# the location of the app is given by ``path`` option
			self.mtime = os.stat(self.mpath).st_mtime
			path, modname = os.path.split(self.mpath)
			modname = modname.split(".py")[0]
			m = imp.load_module(modname, \
					*imp.find_module(modname, [path]))

			if self.class_:
				try:
					self.body = m.__getattribute__(self.class_)(xenviron)
				except AttributeError, e:
					# XXX: this is also raised on AttributeError in app's constructor
					raise ApplicationNotFoundInModuleError(self.class_,
						where=self.mpath, source="root", msg=e)
			else:
				try:
					self.body = m.load(xenviron)
				except AttributeError, e:
					# XXX: this is also raised on AttributeError in app's constructor
					raise NoApplicationExistsError(path, source=self.cpath, msg=e)

	# XXX: Not used right now
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
		# if body is not loaded/not recent, load/reload it
		if not self.body or self._is_modified():
			try:
				applist_lock.acquire()
				self._reload(xenviron)
			finally:
				applist_lock.release()

		return self
		

class Root:
	def __init__(self, meltscriptname=False, debug=False):  	# XXX: meltscriptname is too cryptic
		"""Create the root WSGI application.
		
		* Usually, this constructor is not called by the programmer directly.
		* It is called by ``configure``.
		* Set ``meltscript=True`` when using by another WSGI server.
		* Set ``debug=True`` for debug mode.
		
		"""
		
		self._applist = {}  # all apps
		self._index = None  # index app
		self._error = None
		self.sessionman = SessionManager()
		self.debug = False
		self.meltscriptname = meltscriptname  # XXX: meltscriptname is too cryptic

	def register_app(self, name, cpath):
		"""Register the application if it is not already registered.
		
		* This method is called by ``configure``.		
		* ``cpath`` is the path of the configuration file.
		
			- If the config. files are in cfg/ cpath could be
			``cfg/example.ini``.
		
		"""
		
		if name not in self._applist:
			self._applist[name] = ApplicationInfo(name, cpath=cpath)
		# XXX: maybe we should raise an exception if name is in applist

	# TODO: This is pretty ugly, make it more useful
	def _default_index(self, start_response):
		response = Struct()
		response.content = TextContent(_(u"Index method is left out"))
		response.code = 404
		response.heads = Heads()
		
		return self._prepare_response(start_response, Response(response))
		
	# TODO: This is pretty ugly, make it more useful
	def _default_error(self, start_response, code, message):
		response = Struct()
		response.content = TextContent(message)
		response.code = code
		response.heads = Heads()
		
		return self._prepare_response(start_response, Response(response))

	def __call__(self, environ, start_response):
		# TODO: The error handler must be put here
		return self.run(environ, start_response)

	def run(self, environ, start_response):
		# tuplize query part of the URL
		# /abc?x=1&y becomes (x,1) (y,True)
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
				raise WSGIKeyNotPresentError("SCRIPT_NAME", source="root.py")
			
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
		
		# use Python's ``cgi`` module to parse contents of POST
		try:
			xenviron.fields = BizFieldStorage(environ=environ,
						fp=environ["wsgi.input"])
		except KeyError:
			raise WSGIKeyNotPresentError("wsgi.input")
			
		xenviron.cookies = CookieJar(environ.get("HTTP_COOKIE", ""))
		xenviron.env = environ

		# TODO: Find a way to figure out whether the client browser can use cookies
		try:
			sessionman_lock.acquire()
			try:
				xenviron.cookies, xenviron.session = self.sessionman.get_session(xenviron.cookies)
			except SessionError:
				xenviron.session = self.sessionman.new_session()
		finally:
			sessionman_lock.release()
			
		appname = path[0]

		# if no application name given in the URL (i.e., it is ``/``),
		# ... call the index/default index application
		if not appname:
			if not self._index:
				return self._default_index(start_response)

			appname = self._index
			
		try:
			app = self._applist[appname](xenviron)
		except KeyError, e:
			xenviron.error_code = 404
			if self.debug:
				xenviron.error_message = unicode(e)
			else:
				xenviron.error_message = _(u"Method not found")

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

		try:
			root.debug = cfg.getboolean("root", "debug")
		except (NoSectionError,NoOptionError):
			root.debug = False

		try:
			root._index = cfg.get("root", "index")
		except (NoSectionError,NoOptionError):
			root._index = ""
			
		try:
			root._error = cfg.get("root", "error")
		except (NoSectionError,NoOptionError):
			root._error = ""

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

		return root


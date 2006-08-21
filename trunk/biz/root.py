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


import os.path
import urllib
import threading
from cgi import parse_qsl

from biz.utility import Struct, Heads, CookieJar, BizFieldStorage
from biz.content import TextContent
from biz.response import Response
from biz.session import SessionManager, SessionError
from biz.errors import *
from biz.appinfo import ApplicationInfo

__all__ = ["Root"]

sessionman_lock = threading.Lock()

_ = lambda s: s


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
		self._login = None  # login app
		self.sessionman = SessionManager()
		self.debug = debug
		self.meltscriptname = meltscriptname  # XXX: meltscriptname is too cryptic
		self.cacheall = False

	def register_app(self, name, appoptions):
		"""Register the application if it is not already registered.
		
		* This method is called by ``configure``.		
		* ``appoptions`` is the application options.
		
			- If the config. files are in cfg/ cpath could be
			``cfg/example.ini``.
		
		"""
		
		if name not in self._applist:
			self._applist[name] = ApplicationInfo(name, appoptions)
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
		params = dict([(x[0],x[1] or True)
			for x in parse_qsl(environ["QUERY_STRING"], keep_blank_values=True)])
		
		# a dirty little trick to deny FieldStorage to use QUERY_STRING
		environ["QUERY_STRING"] = ""

		xenviron.path.args = path
		xenviron.path.scriptname = environ["SCRIPT_NAME"]
		xenviron.path.kwargs = params
		
		# use Python's ``cgi`` module to parse contents of POST
		try:
			xenviron.fields = BizFieldStorage(environ=environ,
						fp=environ["wsgi.input"])
		except KeyError:
			raise WSGIKeyNotPresentError("wsgi.input")
			
		xenviron.cookies = CookieJar(environ.get("HTTP_COOKIE", ""))
		xenviron.env = environ

		# TODO: Find a way to check whether the client browser can use cookies
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
							
		try:
			response = app(xenviron)
		except KeyboardInterrupt:
			pass  # sys.exit()
		
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
	def configure(cfgfilename="biz.ini", update=False):
		from biz.cfgutil import BizIniManager
		
		def extbool(x):
			if x.lower() in ["true", "yes", "1"]:
				return True
			elif x.lower() in ["false", "no", "0"]:
				return False
			else:
				return bool(x)
		
		bm = BizIniManager(cfgfilename)
		root = Root()
		
		for k, v in bm.apps.iteritems():
			root.register_app(k, v)
			
		root.debug = extbool(bm.root.get("debug", "no"))
		root._index = bm.root.get("index", "")
		root._error = bm.root.get("error", "")
		root._login = bm.root.get("login", "")
		root.sessionman.timeout = int(bm.root.get("timeout", 0))
		root.sessionman.expiretime = int(bm.root.get("expiretime", 0))
		root.cacheall = extbool(bm.root.get("cacheall", "no"))
				
		return root


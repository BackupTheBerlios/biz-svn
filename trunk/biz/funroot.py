
import urllib
import threading
from cgi import parse_qsl
from biz.utility import Struct, Heads, CookieJar
from biz.content import TextContent
from biz.response import Response
from biz.session import SessionManager, SessionError

__all__ = ["FunRoot"]

sessionman_lock = threading.Lock()
_ = lambda s: s


class FunRoot(object):
	__slots__ = ["sessionman", "meltscriptname", "r"]
	r = threading.local()
	
	def __init__(self, **kwargs):
		self.sessionman = SessionManager()
		self.meltscriptname = kwargs.get("meltscriptname", False)
		
	def __call__(self, environ, start_response):
		return self.run(environ, start_response)
		
	def run(self, environ, start_response):
		try:	
			path_info = urllib.unquote_plus(environ["PATH_INFO"])
		except KeyError:
			path_info = ""
		
##		self.r = r
##		r = Struct()
		r = self.r
		r.path = Struct()
		r.path.endswithslash = path_info.endswith("/")
		
		if not self.meltscriptname:
			try:
				path_info = "%s%s" % (environ["SCRIPT_NAME"],path_info)
			except KeyError:
				pass
			
		path = [p for p in path_info.split("/") if p] or [""]
		
		if self.meltscriptname:
			try:
				r.path.scriptname = environ["SCRIPT_NAME"]
			except KeyError:
				pass
		else:
			r.path.scriptname = ""
			
		kwargs = dict([(x[0],x[1])
			for x in parse_qsl(environ["QUERY_STRING"], keep_blank_values=True)])
		
		r.cookies = CookieJar(environ.get("HTTP_COOKIE", ""))
		r.env = environ

		# TODO: Find a way to figure out whether the client browser can use cookies
		try:
			sessionman_lock.acquire()
			try:
				r.cookies, r.session = self.sessionman.get_session(r.cookies)
			except SessionError:
				r.session = self.sessionman.new_session()
		finally:
			sessionman_lock.release()
			
		appname = path[0]
		args = path[1:]
		
		if not (appname and hasattr(self, appname)):
			appname = "__index__"
			
		r.heads = Heads()
		r.code = 200
		
		try:
##			response = getattr(self, appname)(r, *args, **kwargs)
			getattr(self, appname)(*args, **kwargs)
		except TypeError, e:
			response = getattr(self, "__error__")(r, e)
		
		try:
			sessionman_lock.acquire()
			# further process the app_xenviron
##			self.sessionman.update(response.session)
			self.sessionman.update(r.session)
		finally:
			sessionman_lock.release()

##		return self._prepare_response(start_response, Response(response))
		return self._prepare_response(start_response, Response(r))
		
	def _prepare_response(self, start_response, response):
		rc, rh, ct = response.get_forwsgi()
		start_response(rc, rh)
		return ct
		
	def __index__(self, r):
		r.content = TextContent(_(u"Index method is left out"))
		r.code = 404		
		return r
		
	def __error__(self, r, e):
		r.content = TextContent(e)
		r.code = 500
		return r
	

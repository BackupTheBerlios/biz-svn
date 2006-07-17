
import urllib
from biz.utility import Struct, Heads
from biz.content import TextContent
from biz.response import Response

__all__ = ["MiniRoot"]


class MiniRoot(object):
	def __call__(self, environ, start_response):
		return self.run(environ, start_response)
		
	def run(self, environ, start_response):
		try:	
			path_info = urllib.unquote_plus(environ["PATH_INFO"])
		except KeyError:
			path_info = ""
		
		path = [p for p in path_info.split("/") if p] or [""]

		appname = path[0]
		path = path[1:]
		
		if not (appname and hasattr(self, appname)):
			appname = "__index__"
			
		r = Struct(env=environ, heads=Heads(), code=200)
		
		try:
			response = getattr(self, appname)(r, *path)
		except Exception, e:
			response = getattr(self, "__error__")(r, e)
		
		return self._prepare_response(start_response, Response(response))
		
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
	


import urllib
from biz.utility import Struct, Heads, shift_path
from biz.content import TextContent
from biz.response import Response

__all__ = ["MiniRoot"]

_ = lambda s: s

class MiniRoot(object):
    def __call__(self, environ, start_response):
        return self.run(environ, start_response)
        
    def run(self, environ, start_response):
        environ["PATH_INFO"] = urllib.unquote_plus(environ["PATH_INFO"])
        appname = shift_path(environ)
        print appname
        
        if not appname:
            appname = "_index_"
            
        r = Struct(env=environ, heads=Heads(), code=200)

        try:
            app = getattr(self, appname)
        except AttributeError:
            app = getattr(self, "_default_")
            
        try:
            response = app(r)
        except Exception, e:
            response = getattr(self, "_error_")(r, e)
        
        return self._prepare_response(start_response, Response(response))
        
    def _prepare_response(self, start_response, response):
        rc, rh, ct = response.get_forwsgi()
        start_response(rc, rh)
        return ct
        
    def _index_(self, r):
        r.content = TextContent(_(u"Index method is left out"))
        r.code = 404        
        return r
        
    def _error_(self, r, e):
        r.content = TextContent(str(e))
        r.code = 500
        return r
    
    def _default_(self, r):
        content = "\n".join("%s=%s" % kv for kv in r.env.iteritems())
        r.content = TextContent(content)
        return r

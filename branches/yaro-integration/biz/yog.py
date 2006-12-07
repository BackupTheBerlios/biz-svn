# -*- coding: utf-8 -*-

"""Yoghurt uilities; adapted from Yaro."""

from biz.responses import RESPONSES


class Request(object):
    """Yet another request object (for WSGI), as advertised."""
    
    def __init__(self, environ, start_response, extra_props=None):
        """Set up the various attributes."""
        self.environ = environ
        self._start_response = start_response
        self.start_response_called = False
        self.method = environ['REQUEST_METHOD']
        self.content_type = environ.get('CONTENT_TYPE', '')
        self.content_length = environ.get('CONTENT_LENGTH', '')
##        self.uri = URI(environ)
##      self.res = Response(self.uri())
##      self._parse_query()
        if extra_props is not None:
            for prop_spec in extra_props:
                self.load_prop(*prop_spec)
        self.exc_info = None
        
    def start_response(self, *a, **kw):
        """Wrap the real start_response and set flag when called.

        This provides a means to prevent the real start_response from 
        getting called more than once.

        The flag is self.start_response_called = True|False.
        """
        self.start_response_called = True
        return self._start_response(*a, **kw)
        
    def load_prop(self, attr_name, key, default=None):
        """Add an arbitrary property."""
        if isinstance(key, str):
            value = self.environ.get(key, default)
        else:
            value = key(self.environ)
        setattr(self, attr_name, value)
        
    def forward(self, app):
        """Forward the request to another Yaro compatible handler."""
        return app(self)
        
    def wsgi_forward(self, wsgiapp):
        """Forward the request to a WSGI compatible handler."""
        return wsgiapp(self.environ, self.start_response)
        
    def __getattr__(self, attr):
        """Support lazy loading of form or body."""
        if attr == 'form' and not 'form' in self.__dict__:
            self._parse_form()
        elif attr == 'body' and not 'body' in self.__dict__:
            self._load_body()
        elif attr == 'cookie' and not 'cookie' in self.__dict__:
            self._load_cookie()
        return self.__dict__[attr]
        
    def _load_body(self):
        """Set self.body with the raw body of the request."""
        clen = self.environ.get('CONTENT_LENGTH', 0)
        if clen:
            self.body = self.environ['wsgi.input'].read(int(clen))
        else:
            self.body = ""
            
    def _load_cookie(self):
        """Set self.cookie with a populated Cookie.SimpleCookie."""
        self.cookie = Cookie.SimpleCookie()
        self.cookie.load(self.environ.get('HTTP_COOKIE', ''))
        
            
class Response(object):
    """Hold on to info about the response to a request."""
    
    def __init__(self, content="", status=200, **headers):
        self.headers = headers
        self.status = status  ##'200 OK'
        self.content = content
        
    def _resolve(self):
        # convert all headers to lower case, replace _ with -
        heads = self.headers
        heads = dict([(k.replace("_", "-").lower(),v) for k,v in heads.iteritems()])
        if not "content-type" in heads:
            heads["content-type"] = "text/plain"
            
        self.headers = list(heads.iteritems())
        self.status = "%d %s" % (self.status,RESPONSES.get(self.status, [""])[0])
        

def isiterable(it):
    try:
        iter(it)
    except:
        return False
    else:
        return True


class AbortSignal(Exception):
    def __init__(self, status, message=""):
        self.status = status
        self.message = message
        
        
def abort(status, message=""):
    raise AbortSignal(status, message)
        

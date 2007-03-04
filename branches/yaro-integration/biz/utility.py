# utility.py

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

import cgi
import os.path

class Struct:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
        self.__contains__ = self.__dict__.__contains__
        self._get = self.__dict__.get       
        self._has_key = self.__dict__.has_key

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def _getdict(self):
        return dict([(k,v) for 
                k,v in self.__dict__.iteritems() if not k.startswith("_")])

    def _getlist(self):
        return [(k,v) for 
                k,v in self.__dict__.iteritems() if not k.startswith("_")]
                

class Heads(Struct):
    def _getlist(self):
        r = []
        for k, v in self.__dict__.iteritems():
            if k.startswith("_"):
                continue
                
            k = k.replace("_", "-")
            if isinstance(v, list):
                r.extend([(k,str(vx)) for vx in v])
            else:
                r.append((k,str(v)))
                
        return r

class Cookie:
    def __init__(self, cookiename, value, **kwargs):
        self.name = cookiename
        self.value = value
        # XXX: find a better name for ``values``
        self.values = kwargs
        
    def __getitem__(self, key):
        return self.values[key]
        
    def __setitem__(self, key, value):
        self.values[key] = value
        
    def __repr__(self):
        return "%s=%s; %s" % (self.name,str(self.value),
            " ".join(["%s=%s;" % (k.capitalize(),str(v))
                for k,v in self.values.iteritems()]))
            

class CookieJar:
    def __init__(self, cookiestring=""):
        self.cookies = self._process_cookiestring(cookiestring)
        self.__contains__ = self.cookies.__contains__
        
    def _process_cookiestring(self, cookiestring):
        def g(kv):
            return (kv[0],Cookie(kv[0],kv[1]))
            
        morsels = [g(x.strip().split("=")) for x in cookiestring.split(";") if x]
        return dict(morsels)
        
    def __getitem__(self, key):
        return self.cookies[key]
        
    def __setitem__(self, key, value):
        self.cookies[key] = Cookie(key, value)
        
    def __delitem__(self, key):
        del self.cookies[key]
        
    def add(self, cookiename, value, **kwargs):
        self.cookies[cookiename] = Cookie(cookiename, value, **kwargs)
        
    def modify(self, cookie):
        self.cookies[cookie.name] = cookie
        
    def remove(self, cookiename):
        del self.cookies[cookiename]
        
    def update(self, cookiejar):
        self.cookies.update(cookiejar.cookies)
        
    def getlist(self):
        return [str(v) for v in self.cookies.values()]


class DataGroup(dict):
    def __init__(self, **kwargs):
        def notfound(k):
            self.missing.add(k)
            return ""
            
        st = self.__setitem__
        self.missing = set()
        for k, v in kwargs.iteritems():
            if isinstance(v, list):
                for vv in v:
                    val = vv.get(k)
                    if val:
                        st(k, val)
                        break
                else:
                    st(k, notfound(k))
            else:
                st(k, v.get(k) or notfound(k))


class RedirectionSignal(Exception):
    def __init__(self, location, permanent=False):
        self.location = location
        self.status = permanent and 301 or 307
        

class UrlFor(object):
    def __init__(self, baseurl=""):
        self.set_baseurl(baseurl)
        
    def set_baseurl(self, baseurl):
        self.__baseurl = baseurl.rstrip("/")
        
    def urlFor(self, app="", *handlers, **kwargs):
        """Return absolute URL.
        + *app*: name of the application (string), don't prepend/append `/`
        + *handlers*: handlers (list), don't prepend/append `/`
        + *kwargs*: named parameters (FIXME)
        
        *handlers* are ignored if *app* is not specified.
        
        >>> url = UrlFor("http://localhost:8000")
        >>> url.urlFor()
        'http://localhost:8000/'
        >>> url.urlFor("welcome")
        'http://localhost:8000/welcome'
        >>> url.urlFor("", "welcome")
        'http://localhost:8000/'
        >>> url.urlFor("image", "show")
        'http://localhost:8000/image/show'
        >>> url.urlFor("image", "show", "1")
        'http://localhost:8000/image/show/1'
        >>> url.urlFor("image", "show", "1", orient="horizontal")
        'http://localhost:8000/image/show/1?orient=horizontal'
        >>> url.urlFor("image", "show", "1", orient="horizontal", thumb="yes")
        'http://localhost:8000/image/show/1?orient=horizontal&thumb=yes'
        >>> url.urlFor("welcome/image")
        'http://localhost:8000/welcome/image'
        >>>
        """
        p1 = app and ("/".join([self.__baseurl, app.strip("/")] + [h.strip("/") for h in handlers])) \
                or "/".join([self.__baseurl, ""])
        return kwargs and ("?".join([p1, "&".join(["%s=%s" % kv for kv in kwargs.iteritems()])])) \
                or p1
                
    def redirectTo(self, url, permanent=False):
        raise RedirectionSignal(url, permanent)


class PathFor(object):
    def __init__(self, basepath=""):
        self.set_basepath(basepath)
        
    def set_basepath(self, basepath):
        self.__basepath = basepath
        
    def pathFor(self, path):
        """Return absolute path.
        """
        return os.path.join(self.__basepath, path)

def shiftPath(env):
    if env["PATH_INFO"] in ["", "/"]:
        return ""
    pi = env["PATH_INFO"].split("/", 2)
    env["SCRIPT_NAME"] = "/".join([env["SCRIPT_NAME"],pi[1]])
    try:
        env["PATH_INFO"] = "".join(["/", pi[2]])
    except IndexError:
        env["PATH_INFO"] = ""

    return pi[1]
    
def get_baseurl(env):
    url_scheme = env.get("wsgi.url_scheme", "http")
    remote_addr = env["REMOTE_ADDR"]
    scr_name = env["SCRIPT_NAME"]
    port = env.get("SERVER_PORT", "")
    if (url_scheme == "http" and port in ["", "80"]) or \
            (url_scheme == "https" and port in ["", "443"]):
        port = ""
    else:
        port = ":" + port
    return "".join([url_scheme, "://", remote_addr, port, scr_name])
    
def getFieldStorage(request):
    return cgi.FieldStorage(environ=request.environ, 
            fp=request.environ["wsgi.input"])
    
def _test():
    import doctest
    doctest.testmod()
    
if __name__ == "__main__":
    _test()


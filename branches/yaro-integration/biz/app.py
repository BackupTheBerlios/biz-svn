# -*- coding: utf-8 -*-
# app.py -- Biz application

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

import re
import types
from biz.utility import Struct, Heads, popPath
from biz.errors import *

__all__ = ["ArgHandler", "Application"]

# TODO: Needs i18n here
_ = lambda s: s

_urlsp = re.compile(r"\[:(.*?):\]")
_urlspDict = dict(
                  appname="biz.appname",
                  baseurl="biz.baseurl",
                  url_scheme="wsgi.url_scheme",
                  server_name="SERVER_NAME",
                  server_port="SERVER_PORT",
                  script_name="SCRIPT_NAME",
                  path_info="PATH_INFO",
                  remote_addr="REMOTE_ADDR"
                  )

def _urlspFun(env, text):
    return _urlsp.sub(lambda m: env[_urlspDict[m.group(1)]], text)
                  

class ArgHandler:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
    def __call__(self, req):
        self.__req = req
        return self.dynamic(req)
        
    def dynamic(self, req):
        """
        This method is called on each call.
        + Override this
        + Put dynamic content here
        """
        pass

    def urlSub(self, url):
        """
        Special sequences (only for *first*):
        + {:appname:}: application's name (env["biz.appname"])
        + {:baseurl:}: base URL (the part until appname) (env["biz.baseurl"])
        + {:handler_name:}: env["biz.handler_name"][:-7] (not implemented)
        + {:url_scheme:}: env["wsgi.url_scheme"]
        + {:server_name:}: env["SERVER_NAME"]
        + {:server_port:}: env["SERVER_PORT"]
        + {:script_name:}: env["SCRIPT_NAME"]
        + {:path_info:}: env["PATH_INFO"]
        + {:remote_addr:}: env["REMOTE_ADDR"]
        """
        env = self.__req.environ
        return _urlsp.sub(lambda m: env[_urlspDict[m.group(1)]], url)
    
    def urlFor(self, first="", *args, **kwargs):
        """
        urlFor() -> app=current, handler=current
        urlFor("/") -> app=index, handler=default
        urlFor("abc") -> app=current, handler=abc
        urlFor("/abc") -> app=abc, handler=default
        urlFor("abc", "def") -> app=abc, handler=def
        urlFor("/abc", "def/ghj") -> app=abc, handler=def/ghj

        >>> handler(
        """
        env = self.__req.environ
        base = env["biz.baseurl"]; scrname = env["SCRIPT_NAME"]
        if first.startswith("/"):
            p1 = "/".join([base + first] + list(args))
        elif first.startswith("#"):
            a, b = popPath(scrname)
            a = a.rstrip("/")
            p1 = "/".join(["".join([base, a, "/", first.lstrip("#").lstrip()])] + list(args))
        else:
            if not first:
                p1 = base + scrname
            else:
                p1 = "/".join([base + scrname, first] + list(args))
        
        return kwargs and ("?".join([p1, "&".join(["%s=%s" % kv for kv in kwargs.iteritems()])])) \
                or p1

        
class Application:
    def __init__(self, environ):
##        self.q = q = Struct()
##        q.options = environ["biz.options"]
##        q.appname = environ["biz.appname"]
        environ["biz.q"] = Struct()
        self.environ = environ
        self.static()

    def static(self):
        """prepare static content
        * This method is called once on application creation
        """
        pass

    def __call__(self, req):
        environ = req.environ
        handler_name = "%sHandler" % shiftPath(environ)
        try:
            handler = getattr(self, handler_name)
        except AttributeError:
            abort(404, _(u"%s not found") % environ["SCRIPT_NAME"])
            
        if isinstance(handler, types.ClassType):  # XXX: won't catch C(object)
            handler = handler()

        environ["biz.options"] = self.environ["biz.options"]
        environ["biz.q"] = self.environ["biz.q"]
        environ["biz.handler_name"] = handler_name
        return handler(req)

    class Handler(ArgHandler):
        def dynamic(self, req):
            abort(404, _(u"%s not found") % req.environ["SCRIPT_NAME"])


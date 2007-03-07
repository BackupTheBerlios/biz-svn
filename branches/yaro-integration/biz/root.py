# -*- coding: utf-8 -*-
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

import __builtin__
from biz.utility import Struct, Heads, shiftPath, UrlFor, get_baseurl, \
        PathFor, RedirectionSignal, getFieldStorage
from biz.errors import *
from biz.appinfo import ApplicationInfo
from biz.yog import Response, Request, AbortSignal, abort, isiterable
try:
    from wsgiref.util import FileWrapper
except ImportError:
    print "Instead of wsgiref, local util is used"
    from biz.wsgiutil import FileWrapper

__all__ = ["Root"]
_ = lambda s: s


class Root:
    def __init__(self, basepath, debug=False):
        """Create the root WSGI application.        
        * Usually, this constructor is not called by the programmer directly.
        * It is called by ``configure``.
        * Set ``debug=True`` for debug mode.        
        """
        
        self._applist = {}  # all apps
        self._index = None  # index app
        self._error = None
        self._login = None  # login app
        self.debug = debug
        self.cacheall = False
        self.basepath = basepath
        self.url_for = UrlFor()
        
        # inject some useful functions into __builtin__
#        __builtin__.urlFor = self.url_for.urlFor
        __builtin__.redirectTo = self.url_for.redirectTo
        __builtin__.pathFor = PathFor(basepath).pathFor
        __builtin__.abort = abort
        __builtin__.getFieldStorage = getFieldStorage
        __builtin__.shiftPath = shiftPath

    def register_app(self, name, appoptions):
        """Register the application if it is not already registered.        
        * This method is called by ``configure``.       
        * ``appoptions`` is the application options.        
            - If the config. files are in cfg/ cpath could be
            ``cfg/example.ini``.        
        """        
        if name not in self._applist:
            self._applist[name] = ApplicationInfo(name, appoptions)

    def __call__(self, environ, start_response):
        # TODO: The error handler must be put here
##        return self.run(environ, start_response)
        if "biz.request" in environ:
            req = environ["biz.request"]
        else:
            req = Request(environ, start_response)

        try:
            resp = self.run(req)
        except AbortSignal, e:
            resp = Response(e.message)
            resp.status = e.status
        except RedirectionSignal, e:
            resp = Response("", location=e.location)
            resp.status = e.status
            
        if not isinstance(resp, Response):
            if resp is None:
                resp = ""
            resp = Response(resp)
            
        if (not "content-length" in resp.headers) and \
                (isinstance(resp.content, str)):
            resp.headers["content-length"] = str(len(resp.content))                     
            
        resp._resolve()
        content = resp.content

        if not req.start_response_called:
            req.start_response(resp.status, resp.headers, req.exc_info)
        
        if isinstance(content, str):
            return [content]
        elif isiterable(content):
            return content
        else:
            return FileWrapper(content)

    def run(self, req):
        environ = req.environ
        environ["biz.basepath"] = self.basepath
        environ["biz.baseurl"] = baseurl = get_baseurl(environ)
        self.url_for.set_baseurl(baseurl)
        appname = shiftPath(environ)
        
        # if no application name given in the URL (i.e., it is ``/``),
        # ... call the index/default index application
        if not appname:
            if not self._index:
                abort(404, _(u"%s not found") % environ["SCRIPT_NAME"])
            appname = self._index
    
        environ["biz.appname"] = appname
        
        try:
            app = self._applist[appname](environ)
        except KeyError, e:
            abort(404, _(u"%s not found") % environ["SCRIPT_NAME"])
                        
        return app(req)
        
    @staticmethod
    def configure(cfgfilename="biz.ini", update=False):
        import os
        import os.path
        from biz.cfgutil import BizIniManager
        
        def extbool(x):
            if x.lower() in ["true", "yes", "1"]:
                return True
            elif x.lower() in ["false", "no", "0"]:
                return False
            else:
                return bool(x)
        
        basepath = os.path.dirname(cfgfilename) or os.getcwd()
        bm = BizIniManager(cfgfilename)
        root = Root(basepath=basepath)
        
        for k, v in bm.apps.iteritems():
            root.register_app(k, v)
            
        root.debug = extbool(bm.root.get("debug", "no"))
        root._index = bm.root.get("index", "")
        root._error = bm.root.get("error", "")
        root._login = bm.root.get("login", "")
##        root.sessionman.timeout = int(bm.root.get("timeout", 0))
##        root.sessionman.expiretime = int(bm.root.get("expiretime", 0))
        root.cacheall = extbool(bm.root.get("cacheall", "no"))
                
        return root


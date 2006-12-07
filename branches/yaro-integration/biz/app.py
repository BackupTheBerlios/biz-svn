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

import types
from biz.utility import Struct, Heads, shift_path
from biz.errors import *

__all__ = ["ArgHandler", "Application"]

# TODO: Needs i18n here
_ = lambda s: s


class ArgHandler:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
    def __call__(self, req):
        return self.dynamic(req)
        
    def dynamic(self, req):
        """
        This method is called on each call.
        * Override this
        * Put dynamic content here
        """
        pass
        
        
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
        handler_name = "%sHandler" % shift_path(environ)
        try:
            handler = getattr(self, handler_name)  # TODO: try...except here
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


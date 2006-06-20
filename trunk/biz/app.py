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


from biz.response import Response
from biz.utility import Struct, Heads
from biz.errors import *

from biz.content import TextContent, EmptyContent

__all__ = ["ArgHandler", "CompositeArgHandler",
			"Application", "StaticApplication"] ##, "SecureApplication"]


# TODO: Needs i18n here
_ = lambda s: s


class ArgHandler:
	def __init__(self, parent, name, **kwargs):
		self.parent = parent
		self.name = name
		self.__dict__.update(kwargs)
		
	def __call__(self, request):
		self.r = request
		self.r.content = TextContent(_(u"handler default"))
		self.r.code = 200
		self.r.heads = Heads()
		
		try:
			self.dynamic()
		except Exception, e:
			raise ApplicationDynamicError(e.args, where=self.name, source=__file__)
		
		return self.r
		
	def dynamic(self):
		"""
		This method is called on each call.
		* Override this
		* Put dynamic content here
		"""
		pass
		
	def redirect(self, location, permanent=False):
		if permanent:
			self.r.code = 301
		else:
			self.r.code = 307
		self.r.heads.location = location
		self.r.content = EmptyContent()
		
		
class CompositeArgHandler(ArgHandler):
	def __call__(self, request):
		self.r = request
		path = self.r.path
		try:
			# XXX: Need validation here for request.args[1]
			handler = getattr(self, "%sHandler" % path.args[0])(self, "%sHandler" % path.args[0], q=self.q, p=self.p)
			path.prevargs += [path.args[0]]  # /app[0]/handler1[1]/param1[2]/...
			path.args = path.args[1:]
				
			return handler(self.r)
			
		except (IndexError, AttributeError):
			return self.__handle(self.r)
			
	def __handle(self, request):
		return ArgHandler.__call__(self, request)
		

class Application:
	def __init__(self, xenviron):
		self.name = xenviron.path.args[0]
		self.q = Struct()
		self.q.options = xenviron.options
		self.q.scriptname = xenviron.path.scriptname
		try:
			self.static()
		except Exception, e:
			raise ApplicationStaticError(e)

	def static(self):
		"""prepare static content

		* Override this method to prepare content that will be prepared once
		"""
		pass

	def __call__(self, request):
		try:
			args = request.path.args
			if len(args) > 1 and hasattr(self, "%sHandler" % args[1]):
				handler_name = "%sHandler" % args[1]
				_prevargs = args[:2]
				_args = args[2:]
			else:
				handler_name = "Handler"
				_prevargs = [args[0]]
				_args = args[1:]
					
			handler = getattr(self, handler_name)(self, handler_name,
								q=self.q, p=Struct())
								
			request.path.prevargs = _prevargs
			request.path.args = _args
			
			response = handler(request)
		except Exception, e:
			raise ApplicationError(self.name, where=handler_name, info=e)
			
		# assure that response is of type ``Struct``
		if not isinstance(response, Struct):
			raise ApplicationError(handler_name, msg=_(u"%(handler) did not return a valid response" % handler_name))
			
		return response
			

	class Handler(ArgHandler):
		def dynamic(self):
			r = self.r
			r.code = 404
			r.content = TextContent(_(u"%s not found") % \
							r.path.args)


class StaticApplication:
	pass

## class StaticApplication:
## 	def __init__(self, xenviron):
## 		self.options = xenviron.options
## 		self.response = Struct()
## 		self.response.code = 200
## 		self.response.content = TextContent(_(u"application default"))
## 		self.response.session = xenviron.session
## 		self.response.cookies = xenviron.cookies
## 		self.response.heads = Heads()
## 		
## 		self.static()
## 		
## 	def static(self):
## 		pass
## 		
## 	def __call__(self, request):
## 		return self.response
## 		

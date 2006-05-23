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
		self.options = kwargs
		self.response = Struct()
		self.response.content = TextContent(_(u"handler default"))
		self.response.code = 200
		self.response.heads = Heads()
		
	def __call__(self, request):
		self.request = request
		self.response.session = request.session
		self.response.cookies = request.cookies
		
		try:
			self.dynamic()
		except Exception, e:
			raise ApplicationDynamicError(e, where=self.name, source=__file__)
		
		return self.response
		
	def dynamic(self):
		"""
		This method is called on each call.
		* Override this
		* Put dynamic content here
		"""
		pass
		
	def redirect(self, location, permanent=False):
		if permanent:
			self.response.code = 301
		else:
			self.response.code = 307
		self.response.heads.location = location
		self.response.content = EmptyContent()
		
		
class CompositeArgHandler(ArgHandler):
	def __call__(self, request):
		args = request.path.args
		try:
			# XXX: Need validation here for request.args[1]
			handler = getattr(self, "%sHandler" % args[0])(self, "%sHandler" % args[0])
			request.path.prevargs = request.path.prevargs + [args[0]]  # /app[0]/handler1[1]/param1[2]/...
			request.path.args = args[1:]
				
			return handler(request)
			
		except (IndexError, AttributeError):
			return self.__handle(request)
			
	def __handle(self, request):
		return ArgHandler.__call__(self, request)
		

class Application:
	def __init__(self, xenviron):
		self.options = xenviron.options
		self.name = xenviron.path.args[0]
		self.scriptname = xenviron.path.scriptname
		self.static()

	def static(self):
		"""prepare static content

		* Override this method to prepare content that will be prepared once
		"""
		pass

	def __call__(self, request):
		args = request.path.args
		try:
			# XXX: Need validation here for request.args[1]
			handler = getattr(self, "%sHandler" % args[1])(self, "%sHandler" % args[1])
			request.path.prevargs = args[:2]  # /app[0]/handler1[1]/param1[2]/...
			request.path.args = args[2:]
		except (IndexError, AttributeError):
			handler = self.Handler(self, "Handler")
			request.path.prevargs = [args[0]]
			request.path.args = args[1:]
			
		return handler(request)

	class Handler(ArgHandler):
		def dynamic(self):
			self.code = 404
			self.response.content = TextContent(_(u"%s not found") % \
							self.request.path.args)


class StaticApplication:
	def __init__(self, xenviron):
		self.options = xenviron.options
		self.response = Struct()
		self.response.content = TextContent(_(u"application default"))
		self.response.session = xenviron.session
		self.response.cookies = xenviron.cookies
		self.response.heads = Heads()
		
		self.static()
		
	def static(self):
		pass
		
	def __call__(self, request):
		return self.response
		

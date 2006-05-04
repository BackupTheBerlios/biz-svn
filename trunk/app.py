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

from biz.content import TextContent, EmptyContent

__all__ = ["Application", "SecureApplication"]


class Application:
	def __init__(self, xenviron):
		self.options = xenviron.options
		self.content = TextContent("application default")

		self.refresh(xenviron)
		self.static()

	def refresh(self, xenviron):
		"""prepare the application to run

		* Extend this method, if you require custom preparation
		"""
		self.args = xenviron.args
		self.kwargs = xenviron.kwargs
		self.session = xenviron.session
		self.cookies = xenviron.cookies
		self.fields = xenviron.fields

		self.code = 200
		self.heads = Heads()

	def static(self):
		"""prepare static content

		* Override this method to prepare content that will be prepared once
		"""
		pass

	def run(self):
		"""execute the application

		* Override this method for dynamic/semi-dynamic content
		* You should supply self.content here with your content,
		* Optionally you may supply self.rcode and/or
		self.rheads
		"""
		pass

	def get(self):
		xenviron = Struct()  # FUTURE
		xenviron.cookies = self.cookies
		xenviron.session = self.session
		return (xenviron,Response(self.code, self.content, **self.heads._getdict()))

	def redirect(self, location):
		self.code = 307
		self.heads.location = location
		self.content = EmptyContent()


class SecureApplication(Application):
	def refresh(self, xenviron):
		Application.refresh(self, xenviron)

		try:
			self.authenticated = self.session.authenticated
			self.userid = self.session.userid
		except:
			self.authenticated = False
			self.userid = None

		if self.authenticated:
			self.run = self.secure_run
			self.static = self.secure_static
		else:
			self.run = self.insecure_run
			self.static = self.insecure_static

	def secure_static(self):
		pass

	def insecure_static(self):
		pass

	def secure_run(self):
		"""

		* Override this for secure parts of your application.
		self.authorized is guaranteed to be True and
		self.userid is guaranteed to contain a valid user id
		"""
		pass

	def insecure_run(self):
		pass
			
		
	

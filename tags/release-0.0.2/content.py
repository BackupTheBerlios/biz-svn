# content.py

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

import os
from cStringIO import StringIO

__all__ = ["EmptyContent", "TextContent", "HtmlContent", 
			"FileContent", "CachedFileContent"]


class Content(object):
	__slots__ = "ctype","_clen"
	
	def __init__(self, ctype):
		self.ctype = ctype
		self._clen = 0
		
	def get(self):
		"""return the content.
		
		* Override this.
		"""
		return None


class TextContent(Content):
	__slots__ = "content"
	
	def __init__(self, content=u""):
		Content.__init__(self, "text/plain")
		self.content = str(content)
		self._clen = len(self.content)
		
	def get(self):
		return [self.content]


class EmptyContent(TextContent):
	def __init__(self):
		TextContent.__init__(self, u"")


class HtmlContent(TextContent):
	def __init__(self, content=u""):
		TextContent.__init__(self, content)
		self.ctype = "text/html"
		
		
class FileContent(Content):
	__slots__ = "_descriptor"

	def __init__(self, filename, ctype):
		Content.__init__(self, ctype)
		self._descriptor = file(filename, "rb")
		self._clen = os.stat(filename).st_size
		
	def get(self):
		return self._descriptor


class CachedFileContent(Content):
	__slots__ = "content"
	
	def __init__(self, filename, ctype):
		Content.__init__(self, ctype)
		
		f = file(filename, "rb")
		self.content = f.read()
		self._clen = len(self.content)

	def get(self):
		return [self.content]



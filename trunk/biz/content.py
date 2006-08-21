# -*- coding: utf-8 -*-
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
import mimetypes

__all__ = ["EmptyContent", "TextContent", "HtmlContent", "XmlContent",
			"FileContent", "CachedFileContent", "CachedContent"]


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
	__slots__ = "content","encoding"
	
	def __init__(self, content, ctype="", encoding="utf-8"):
		ctype = "%s; charset=%s" % (ctype or "text/plain",encoding)
		Content.__init__(self, ctype)
		
		assert isinstance(content, basestring), "content should be a string."
		
		if isinstance(content, unicode):
			self.content = unicode.encode(content, encoding)
		else:
			self.content = content
			
		self._clen = len(self.content)
		self.encoding = encoding
		
	def get(self):
		return self.content


class EmptyContent(TextContent):
	def __init__(self):
		TextContent.__init__(self, u"")


class HtmlContent(TextContent):
	def __init__(self, content, encoding="utf-8"):
		TextContent.__init__(self, content, "text/html", encoding)


class XmlContent(TextContent):
	def __init__(self, content, encoding="utf-8"):
		TextContent.__init__(self, content, "text/xml", encoding)


## class XHtmlContent(TextContent):
## 	def __init__(self, content, encoding="utf-8"):
## 		TextContent.__init__(self, content, "text/xhtml", encoding)
		self.ctype = "text/xhtml"


class FileContent(Content):
	__slots__ = "_descriptor"

	def __init__(self, filename, ctype=None):
		ctype = ctype or mimetypes.guess_type(filename)[0]
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


class CachedContent(Content):
	__slots__ = "content"
	
	def __init__(self, content, ctype):
		Content.__init__(self, ctype)
		self.content = content
		self._clen = len(content)
		
	def get(self):
		return [self.content]

		
		
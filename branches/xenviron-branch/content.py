# content.py

import os
from cStringIO import StringIO

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



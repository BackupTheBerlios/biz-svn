# fileserver.py

import os
import os.path
import mimetypes

from biz.content import TextContent, HtmlContent, FileContent


# XXX: If the last argument is a directory, we have problem with
# URLs not ending with /.
# e.g., biz.png is mapped to /biz.png
class FileServer:
	def __init__(self, location, defaultfile="", defaultindex=False):
		self.location = location
		self.mime_handlers = {}

		assert self.location, \
				"location should be set"
				
		self.defaultfile = defaultfile
		self.defaultindex = defaultindex

		if not self.location.endswith("/"):
			self.location += "/"

		self.code = 404
		self.content = TextContent("Content never set!")
		
	def run(self, path_args):
		path = "/".join(path_args)

		if self.defaultfile:
			path = self.defaultfile
		elif not path and self.defaultindex:
			# XXX: This is problematic!
			path = "index.html"			

		newpath = os.path.join(self.location, path)
		
		self.code = 200
		if os.path.isfile(newpath):
			self.content = self.handle_file(newpath)
		elif os.path.isdir(newpath):
			self.code = 404
			self.content = self.handle_dir(newpath)
		else:
			self.code = 404
			self.content = TextContent("File not found")

	def handle_file(self, fname):
		mime_type = mimetypes.guess_type(fname)[0] or "application/octet-stream"
		self.code = 200
		try:
			return self.mime_handlers[mime_type](fname)
		except KeyError:
			return FileContent(fname, mime_type)

	def handle_dir(self, folder):
		return TextContent("File not found")

	def add_handler(self, mime_type, function):
		self.mime_handlers[mime_type] = function

	def get(self):
		return (self.code,self.content)



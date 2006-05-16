# vfolder_app.py

import os
import os.path
import glob
import mimetypes

## from biz.app import Application
## from biz.content import TextContent, HtmlContent, FileContent

from biz import *


class VirtualFolder(Application):
	"""	environ["virtualfolder.location"] should point to the
	preferred starting directory
	environ["virtualfolder.wildcard"] may contain the wildcard
	(default: *).
	"""
	def static(self):
		self.location = self.options.get("vfolder.location", "")
		assert self.location, \
				"vfolder.location should be set"

		if not self.location.endswith("/"):
			self.location += "/"
			
		self.wildcard = self.options.get("vfolder.wildcard", "*")
		self.mime_handlers = {}
		
	class Handler(RequestHandler):
		def dynamic(self):
			path_items = self.request.path.args
			path = "/".join(path_items)
			name = "/".join(self.request.path.prevargs)
			newpath = os.path.join(self.app.location, path)
	
			if os.path.isfile(newpath):
				self.response.content = self.app.handle_file(newpath)
	
			elif os.path.isdir(newpath):
				try:
					thelist = glob.glob(os.path.join(newpath, self.app.wildcard))
				except OSError:
					self.response.code = 404
					self.response.content = HtmlContent('<p style="color: red">Directory not found</p>')
					return
		
				dirs = sorted([x for x in thelist if os.path.isdir(x)])
				files = sorted([x for x in thelist if os.path.isfile(x)])

				# not displaying the index correctly (\n 's and \t) because of
				# FileContent; so disabled for now...
## 				for index in [os.path.join(newpath, "index.htm"), os.path.join(newpath, "index.html")]:
## 					if index in files:
## 						self.response.content = self.app.handle_file(index)
## 						return
	
				page = "\n".join(["<html><head><title>Browsing: /%s</title></head><body><ul>" % path,
						"<b>Directories</b>",
						"\n".join([self.app._fformat(newpath, name, x, True) for x in dirs]),
						"<b>Files</b>",
						"\n".join([self.app._fformat(newpath, name, x, True) for x in files]),
						"</ul></body></html>"])
				
				self.response.content = HtmlContent(page)
	
			elif not os.path.exists(newpath):
				self.response.code = 404
				self.response.content = TextContent("File not found")
			else:
				self.response.code = 500
				self.response.content = TextContent("error")

	def _fformat(self, path, xname, name, isdir):
		tail = os.path.split(name)[1]
		href = os.path.join("/"+xname, path[len(self.location):], tail)
		if isdir:
			return '<li><a href="%s">%s</a></li>' % (href,tail)
		else:
			return "<li>%s</li>" % tail

	def handle_file(self, fname):
		mime_type = mimetypes.guess_type(fname)[0] or "application/octet-stream"
		try:
			return self.mime_handlers[mime_type](fname)
		except KeyError:
			return FileContent(fname, mime_type)

	def add_handler(self, mime_type, function):
		self.mime_handlers[mime_type] = function
		

def python_handler(fname):
	from biz.apps.vfolder import pycolorize

	f = file(fname)
	p = pycolorize.Parser(f.read())
	f.close()
	
	return HtmlContent(p.format())

def source_handler(fname):
	return FileContent(fname, "text/plain")

def zip_handler(fname):
	import zipfile

	try:
		f = zipfile.ZipFile(fname)
	except IOError:
		return TextContent("File error")

	page = "\n".join(["<html><head><title>Browsing Inside: %s</title></head>" % os.path.split(fname)[1],
						"<body><ul>",
						"\n".join(["<li>%s</li>" % n for n in f.namelist()]),
						"</ul></body></html>"])
						
	return HtmlContent(page)

def load(xenviron):
	vfolder = VirtualFolder(xenviron)
	vfolder.add_handler("text/x-python", python_handler)
	vfolder.add_handler("application/zip", zip_handler)
	
	for m in ["text/x-csrc", "text/x-chdr", "text/x-c++src", "text/x-c++hdr"]:
		vfolder.add_handler(m, source_handler)
	
	return vfolder



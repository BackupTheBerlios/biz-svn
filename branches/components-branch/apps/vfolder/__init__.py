# vfolder_app.py

import os
import os.path
import glob
import mimetypes

from biz.app import Application
from biz.content import TextContent, HtmlContent, FileContent

class VirtualFolder(Application):
	"""	environ["virtualfolder.location"] should point to the
	preferred starting directory
	environ["virtualfolder.wildcard"] may contain the wildcard
	(default: *).
	"""
	def static(self):
		self.location = self.options.get("vfolder.location", "")
		assert self.location, \
				"virtualfolder.location should be set"

		if not self.location.endswith("/"):
			self.location += "/"
			
		self.wildcard = self.options.get("vfolder.wildcard", "*")
		self.mime_handlers = {}
		
	def run(self):
		path_items = self.path

		##if not path_items:  # registered as index handler or error on /
		##    path = ""
		##    self.name = ""
		##elif not self.environ.has_key("biz.error.code"):  # normal condition
		##    path = "/".join(path_items[1:])
		##    self.name = path_items[0]
		##else:  # registered as error handler
		##    path = "/".join(path_items)
		##    self.name = ""

		path = "/".join(path_items[1:])
		self.name = path_items[0]

		newpath = os.path.join(self.location, path)

		if os.path.isfile(newpath):
			self.handle_file(newpath)

		elif os.path.isdir(newpath):
			try:
				thelist = glob.glob(os.path.join(newpath, self.wildcard))
			except OSError:
				self.rcode = 404
				self.content = HtmlContent('<p style="color: red">Directory not found</p>')
				return
	
			dirs = sorted([x for x in thelist if os.path.isdir(x)])
			files = sorted([x for x in thelist if os.path.isfile(x)])

			for index in [os.path.join(newpath, "index.htm"), os.path.join(newpath, "index.html")]:
				if index in files:
					self.handle_file(index)

			page = "\n".join(["<html><head><title>Browsing: /%s</title></head><body><ul>" % path,
					"<b>Directories</b>",
					"\n".join([self.__fformat(newpath, x, True) for x in dirs]),
					"<b>Files</b>",
					"\n".join([self.__fformat(newpath, x, True) for x in files]),
					"</ul></body></html>"])
			
			self.content = HtmlContent(page)

		elif not os.path.exists(newpath):
			self.rcode = 404
			self.content = TextContent("File not found")
		else:
			self.rcode = 500
			self.content = TextContent("error")

	def __fformat(self, path, name, isdir):
		tail = os.path.split(name)[1]
		href = os.path.join("/"+self.name, path[len(self.location):], tail)
		if isdir:
			return '<li><a href="%s">%s</a></li>' % (href,tail)
		else:
			return "<li>%s</li>" % tail

	def handle_file(self, fname):
		mime_type = mimetypes.guess_type(fname)[0] or "application/octet-stream"
		try:
			self.content = self.mime_handlers[mime_type](fname)
		except KeyError:
			self.content=FileContent(fname, mime_type)

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

def load(root):
	vfolder = VirtualFolder(root)
	vfolder.add_handler("text/x-python", python_handler)
	vfolder.add_handler("application/zip", zip_handler)
	
	for m in ["text/x-csrc", "text/x-chdr", "text/x-c++src", "text/x-c++hdr"]:
		vfolder.add_handler(m, source_handler)
	
	return vfolder



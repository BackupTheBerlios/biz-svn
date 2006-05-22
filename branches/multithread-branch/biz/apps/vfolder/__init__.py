# vfolder_app.py

import sys  # REMOVE
import os
import os.path
import glob
import mimetypes

from biz import *
from biz.template import Template


class VirtualFolder(Application):
	"""
	* vfolder.location should point to the preferred starting directory
	* vfolder.wildcard may contain the wildcard (default: *).
	* vfolder.template may point to the template (default: apps/vfolder/vfolder.tmpl)
	"""
	class NamedLocation:
		def __init__(self, path, xname, name, applocation):
			tail = os.path.split(name)[1]
			self.href = os.path.join("/"+xname, path[len(applocation):], tail)
			self.name = tail
			
	def static(self):
		self.location = self.options.main.get("vfolder.location", "")
		assert self.location, \
				"vfolder.location should be set"

		if not self.location.endswith("/"):
			self.location += "/"
			
		self.wildcard = self.options.main.get("vfolder.wildcard", "*")
		self.mime_handlers = {}
		
		templ = self.options.main.get("vfolder.template",
					os.path.join(os.path.dirname(__file__), "vfolder.tmpl"))
		self.template = Template.from_file(templ)
		
	class Handler(ArgHandler):
		def dynamic(self):
			path = self.request.path
			pathstr = "/".join(path.args)
			name = os.path.join(path.scriptname.strip("/"), "/".join(path.prevargs))
			newpath = os.path.join(self.app.location, pathstr)
			
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

				template = self.app.template.copy(True)
				template["title"] = "Browsing: /%s" % pathstr
				template["header"] = "Browsing: /%s" % pathstr
				template["label_dirs"] = "Directories"
				template["label_files"] = "Files"
				template["dirs"] = [self.app.NamedLocation(newpath, name, x, self.app.location) for x in dirs]
				template["files"] = [self.app.NamedLocation(newpath, name, x, self.app.location) for x in files]
				
				self.response.content = HtmlContent(str(template))
	
			elif not os.path.exists(newpath):
				self.response.code = 404
				self.response.content = TextContent("File not found")
			else:
				self.response.code = 500
				self.response.content = TextContent("error")

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

## def zip_handler(fname):
## 	import zipfile

## 	try:
## 		f = zipfile.ZipFile(fname)
## 	except IOError:
## 		return TextContent("File error")

## 	page = "\n".join(["<html><head><title>Browsing Inside: %s</title></head>" % os.path.split(fname)[1],
## 						"<body><ul>",
## 						"\n".join(["<li>%s</li>" % n for n in f.namelist()]),
## 						"</ul></body></html>"])
## 						
## 	return HtmlContent(page)

def load(xenviron):
	vfolder = VirtualFolder(xenviron)
	vfolder.add_handler("text/x-python", python_handler)
##	vfolder.add_handler("application/zip", zip_handler)
	
	for m in ["text/x-csrc", "text/x-chdr", "text/x-c++src", "text/x-c++hdr"]:
		vfolder.add_handler(m, source_handler)
	
	return vfolder



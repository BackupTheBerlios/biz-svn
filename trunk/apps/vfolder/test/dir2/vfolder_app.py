# vfolder_app.py

import os
import os.path
import glob
import mimetypes
from biz.response import Response, TextContent, HtmlContent, FileContent

class VirtualFolder:
	def __init__(self, environ, start_response, location, wildcard="*"):
		self.environ = environ
		self.start_response = start_response

		self.location = location
		if not self.location.endswith("/"):
			self.location += "/"
			
		self.wildcard = wildcard
		self.mime_handlers = {}
##		self.pathre = re.compile(r"([\w/]*)\??(.*)")
		
	def __call__(self):
##		if path == "/":
##			path = ""
		path_items = self.environ["biz.path"]
		path = "/".join(path_items[1:])
		self.name = path_items[0]
		start_response = self.start_response
			
		print "path is:", path
		newpath = os.path.join(self.location, path)
		print "newpath is:", newpath

		if os.path.isfile(newpath):
			return self.handle_file(newpath)
		elif os.path.isdir(newpath):
			try:
	##			dirlist = os.listdir(newpath)
				thelist = glob.glob(os.path.join(newpath, self.wildcard))
			except OSError:
				return Response(self.start_response, code=404,
						content=HtmlContent('<p style="color: red">Directory not found</p>'))
	
			dirs = sorted([x for x in thelist if os.path.isdir(x)])
			files = sorted([x for x in thelist if os.path.isfile(x)])

			for index in [os.path.join(newpath, "index.htm"), os.path.join(newpath, "index.html")]:
				if index in files:
					return self.handle_file(index)

			page = "\n".join(["<html><head><title>Browsing: /%s</title></head><body><ul>" % path,
					"<b>Directories</b>",
					"\n".join([self.__fformat(newpath, x, True) for x in dirs]),
					"<b>Files</b>",
					"\n".join([self.__fformat(newpath, x, True) for x in files]),
					"</ul></body></html>"])
			
			return Response(start_response, content=HtmlContent(page))

		elif not os.path.exists(newpath):
			return Response(start_response, code=404, content=TextContent("File not found"))

		return Response(start_response, code=500, content=TextContent("error"))

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
			return self.mime_handlers[mime_type](self.start_response, fname)
		except KeyError:
			return Response(self.start_response, content=FileContent(fname, mime_type))

	def add_handler(self, mime_type, function):
		self.mime_handlers[mime_type] = function
		

def python_handler(start_response, fname):
	import pycolorize
	f = file(fname)
	p = pycolorize.Parser(f.read())
	f.close()
	
	return Response(start_response, content=HtmlContent(p.format()))

def source_handler(start_response, fname):
	return Response(start_response, content=FileContent(fname, "text/plain"))

def zip_handler(start_response, fname):
	import zipfile
	try:
		f = zipfile.ZipFile(fname)
	except IOError:
		return Response(start_response, code=505, content=TextContent("File error"))

	page = "\n".join(["<html><head><title>Browsing Inside: %s</title></head>" % os.path.split(fname)[1],
						"<body><ul>",
						"\n".join(["<li>%s</li>" % n for n in f.namelist()]),
						"</ul></body></html>"])
						
	return Response(start_response, content=HtmlContent(page))

##funcaller.register("files", Function(DirLister("files", "/home/yuce/dev/python/boz/test/htdocs")))
##dirlister = DirLister("files", "/home/yuce/playground")
	
def run(environ, start_response):
	vfolder = VirtualFolder(environ, start_response, "/home/yuce/dev/python/biz/apps/vfolder/test")
	vfolder.add_handler("text/x-python", python_handler)
	vfolder.add_handler("application/zip", zip_handler)
	
	for m in ["text/x-csrc", "text/x-chdr", "text/x-c++src", "text/x-c++hdr"]:
		vfolder.add_handler(m, source_handler)
	
	return vfolder()

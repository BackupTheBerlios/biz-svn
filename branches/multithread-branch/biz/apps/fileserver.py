# fileserver.py

import biz


class FileServerApp(biz.Application):
	def static(self):
		assert self.options.has_key("fileserver.location"), \
				"fileserver.location should be set for FileServerApp"
				
		defaultfile = self.options.get("fileserver.defaultfile", "")
		
		defaultindex = self.options.get("fileserver.defaultindex", False)

		self.fileserver = biz.FileServer(self.options["fileserver.location"],
						defaultfile, defaultindex)
		
	class Handler(biz.ArgHandler):
		def dynamic(self):
			path = self.request.path
			
			if path.endswithslash:
				fileserver = self.app.fileserver
				fileserver.run(path.args)
				self.response.code, self.response.content = fileserver.get()
			else:
				self.redirect("/%s/" % "/".join(path.prevargs + path.args))


def load(x):
	return FileServerApp(x)

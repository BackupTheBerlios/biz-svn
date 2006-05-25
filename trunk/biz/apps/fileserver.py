# fileserver.py

import biz


class FileServerApp(biz.Application):
	def static(self):
		options = self.options.main
		assert options.has_key("fileserver.location"), \
				"fileserver.location should be set for FileServerApp"
				
		defaultfile = options.get("fileserver.defaultfile", "")
		
		defaultindex = options.get("fileserver.defaultindex", False)

		self.fileserver = biz.FileServer(options["fileserver.location"],
						defaultfile, defaultindex)
		
	class Handler(biz.ArgHandler):
		def dynamic(self):
			path = self.request.path
			
			if path.endswithslash:
				fileserver = self.app.fileserver
				fileserver.run(path.args)
				self.response.code, self.response.content = fileserver.get()
			else:
				self.redirect("/%s/" % "/".join(path.prevargs + path.args), permanent=True)


def load(x):
	return FileServerApp(x)

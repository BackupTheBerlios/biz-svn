# fileserver.py

import biz


class FileServerApp(biz.Application):
	def static(self):
		options = self.q.options.main
		assert options.has_key("location"), \
				"location should be set for FileServerApp"
				
		defaultfile = options.get("defaultfile", "")
		
		defaultindex = options.get("defaultindex", False)

		self.q.fileserver = biz.FileServer(options["location"],
						defaultfile, defaultindex)
		
	class Handler(biz.ArgHandler):
		def dynamic(self):
			q = self.q
			path = self.request.path
			
			if path.endswithslash:
				fileserver = q.fileserver
				fileserver.run(path.args)
				self.response.code, self.response.content = fileserver.get()
			else:
				self.redirect("/%s/" % "/".join(path.prevargs + path.args), permanent=True)


def load(x):
	return FileServerApp(x)

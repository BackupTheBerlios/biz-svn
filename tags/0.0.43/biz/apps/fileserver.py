# fileserver.py

import biz


class FileServerApp(biz.Application):
	def static(self):
		q = self.q
		assert q.options.has_key("location"), \
				"location should be set for FileServerApp"
				
		defaultfile = q.options.get("defaultfile", "")
		
		defaultindex = q.options.get("defaultindex", False)

		q.fileserver = biz.FileServer(options["location"],
						defaultfile, defaultindex)
		
	class Handler(biz.ArgHandler):
		def dynamic(self):
			q = self.q; r = self.r
			path = r.path
			
			if path.endswithslash:
				fileserver = q.fileserver
				fileserver.run(path.args)
				r.code, r.content = fileserver.get()
			else:
				self.redirect("/%s/" % "/".join(path.prevargs + path.args),
						permanent=True)


def load(x):
	return FileServerApp(x)

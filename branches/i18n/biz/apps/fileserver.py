# fileserver.py

import biz


class FileServerApp(biz.Application):
	def static(self):
		assert self.options.has_key("fileserver.location"), \
				"fileserver.location should be set for FileServerApp"

		self.fileserver = biz.FileServer(self.options["fileserver.location"])

	def run(self):
		self.fileserver.run(self.args)
		self.code, self.content = self.fileserver.get()


def load(xenviron):
	return FileServerApp(xenviron)


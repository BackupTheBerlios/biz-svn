# -*- coding: utf-8 -*-

import biz


class CachedFileApp(biz.StaticApplication):
	def static(self):
		assert self.options.main.has_key("cachedfile.path"), \
			"cachedfile.path option is missing"
			
		assert self.options.main.has_key("cachedfile.type"), \
			"cachedfile.type option is missing"
			
		path = self.options.main["cachedfile.path"]
		_type = self.options.main["cachedfile.type"]		
			
		try:
			self.response.content = biz.CachedFileContent(path, _type)
			self.response.code = 200
		except IOError:
			self.response.content = biz.TextContent("File not found")
			self.response.code = 404


def load(x):
	return CachedFileApp(x)

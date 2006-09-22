# -*- coding: utf-8 -*-

import biz


class CachedFile:
	def __init__(self, defaultfile):
		assert defaultfile, \
			"defaultfile should be set"
			
		try:
			self.content = biz.CachedFileContent(defaultfile)
			self.code = 200
		except IOError:
			self.content = _(u"File not found")
			self.code = 404
			
	def get(self):
		return (self.code,self.content)
			
		
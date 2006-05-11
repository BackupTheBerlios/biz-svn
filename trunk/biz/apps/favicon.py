# favicon.py -- Reply a "favicon.ico" request

import biz


class Favicon(biz.Application):
	"""environ["favicon.location"] should point the icon
	(including the filename)
	"""

	def static(self):
		if self.options.has_key(loc, "favicon.location"):
			self.content = biz.CachedFileContent(self.options[loc], "image/x-icon")
			break
		else:
			self.content = biz.EmptyContent()

def load(xenviron):
	return Favicon(xenviron)



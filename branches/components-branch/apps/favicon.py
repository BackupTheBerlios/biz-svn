# favicon.py -- Reply a "favicon.ico" request

from biz.app import Application
from biz.content import FileContent, CachedFileContent, EmptyContent


class Favicon(Application):
	"""environ["biz.app.favicon.location"] should point the icon
	(including the filename),
	environ["biz.app.favicon.default"] may point to the fallback icon.
	"""

	def static(self):
		for loc in ["favicon.location", "favicon.default"]:
			if self.options.has_key(loc):
				self.content = CachedFileContent(self.options[loc], "image/x-icon")
				break
		else:
			self.content = EmptyContent()


def load(root):
	return Favicon(root)



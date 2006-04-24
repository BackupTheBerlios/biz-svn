# favicon.py -- Reply a "favicon.ico" request

from biz.app import Application
from biz.content import FileContent, CachedFileContent, EmptyContent


class Favicon(Application):
	"""self.options["favicon.location"] should point to the icon
	"""

	def static(self):
		locopt = "favicon.location"
		if self.options.has_key(locopt):
			self.content = CachedFileContent(self.options[locopt], "image/x-icon")
			break
		else:
			self.content = EmptyContent()


def load(root):
	return Favicon(root)



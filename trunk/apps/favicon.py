# favicon.py -- Reply a "favicon.ico" request

from biz.app import Application
from biz.content import FileContent, CachedFileContent


class Favicon(Application):
	"""environ["biz.app.favicon.location"] should point the icon
	(including the filename),
	environ["biz.app.favicon.default"] may point to the fallback icon.
	"""

	def static(self):
		environ = self.environ

		for loc in ["biz.app.favicon.location", "biz.app.favicon.default"]:
			if environ.has_key(loc):
				self.content = CachedFileContent(environ[loc], "image/x-icon")
				break
		else:
			self.content = EmptyContent()


def load(environ, start_response):
	environ["biz.app.favicon.default"] = "md5sumgui.ico"
	return Favicon(environ, start_response)



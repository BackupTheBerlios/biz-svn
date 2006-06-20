
import os.path
from biz.app import ArgHandler
from biz.content import FileContent


class FileHandler(ArgHandler):
	def dynamic(self):
		q = self.q
		assert "location" in q[self.name]
		
		args = self.r.path.args
		
		filename = os.path.join(q[self.name]["location"], *args)
		print filename
		
		if os.path.isdir(filename):
			self.r.code = 404
			return
		
		self.r.content = FileContent(filename)
		
		
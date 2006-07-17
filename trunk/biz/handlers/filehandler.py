
import os.path
from biz.app import ArgHandler
from biz.content import FileContent


class FileHandler(ArgHandler):
	def dynamic(self):
		q = self.q; r= self.r
		assert "location" in q[self.name]
		
		args = r.path.args
		
		filename = os.path.join(q[self.name]["location"], *args)
		
		if os.path.isdir(filename):
			r.code = 404
			return
		
		r.content = FileContent(filename)
		
		
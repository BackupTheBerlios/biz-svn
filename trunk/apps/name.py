
from biz.app import Application
from biz.content import HtmlContent


class Name(Application):
	def run(self):
		try:
			template = "Your name is: <b>%(name)s %(surname)s</b>. It's a nice name!"
			name =  self.session.name
			surname = self.session.surname
			self.content = HtmlContent(template % dict(name=name, surname=surname))
			self.session.close()
		except AttributeError:
			try:
				self.session.name = self.params["name"]
				self.session.surname = self.params["surname"]
				self.content = \
						HtmlContent('Your name is saved. You may <a href="%s">continue</a>.' \
						% self.path[0])
			except KeyError:
				page = """<html><head><title>Name</title></head>
						<body><form action="/name" method="get">
						Your name: <input name="name"><br>
						Your surname: <input name="surname"><br>
						<input type="Submit">
						</form></body></html>"""

				self.content = HtmlContent(page)


def load(xenviron):
	return Name(xenviron)


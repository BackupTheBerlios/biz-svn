# sum_app.py

from string import Template

from biz.app import Application
from biz.content import HtmlContent


class SumApp(Application):
	def run(self):
		template = Template(self.options.get("sum.template",
				'The sum is: <b>$sum</b>'))

		page = template.substitute(sum=sum([float(p)
					for p in self.environ["biz.path"][1:]]))

		self.content = HtmlContent(page)


def load(environ, start_response, options):
	return SumApp(environ, start_response, options)


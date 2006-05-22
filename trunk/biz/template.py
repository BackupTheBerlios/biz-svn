# template.py -- Biz templating

# Biz web application framework
# Copyright (C) 2006  Yuce Tekol
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


import re
from collections import deque

from biz.errors import FileNotFoundError

class TemplateNotFoundError(FileNotFoundError):
	pass


class Parser:
	beginline = re.compile(r"^\s*\{%(.*)")
	endline = re.compile(r"^\s*%\}\s*$")
	onelinerline = re.compile(r"^\s*\{%(.*)%\}\s*$")
	chainedline = re.compile(r"^\s*%\}(.*)\{%\s*$")
	
	TEXT, HEADER, END, CHAIN, ONELINER = \
		"text", "header", "end", "chain", "oneliner"
	
	def __init__(self):
		self.handlers = [("chain",self.chainedline),
						("oneliner",self.onelinerline),
						("header",self.beginline),
						("end",self.endline)]
						
		self.items = []

	def handle_header(self, groups):
		code, = groups
		self.items.append((self.HEADER,code.strip()))
		
	def handle_end(self, groups):
		self.items.append((self.END,None))
			
	def handle_chain(self, groups):
		code, = groups		
		self.items.append((self.CHAIN,code.strip()))
		
	def handle_oneliner(self, groups):
		code, = groups
		
		self.items.append((self.ONELINER,code.strip()))
		
	def handle_text(self, text):
		self.items.append((self.TEXT,"".join(text)))
	
	def parse(self, lines):
		text = []
		for line in lines.split("\n"):
			if not line:
				continue
				
			for handler, parser in self.handlers:
				r = parser.search(line)
				if r:
					if text:
						self.handle_text(text)
						text = []
						
					getattr(self, "handle_%s" % handler)(r.groups())
					break
			else:
				text += "%s\n" % line
		
		if text:
			self.handle_text(text)
			text = []


class Template:
	variable = re.compile(r"\$[{]?([a-zA-Z][\w.]*)[}]?")

	def __init__(self, tmpl):
		self.levels = deque()
		self.levels.append(0)

		self.variables = {}
		self._outlist = []
		self.output = tmpl
		self.changed = True
		
		def emitter(*args):
			self._outlist.extend([str(a) for a in args])
			
		self.variables["__emit"] = emitter
		
		parser = Parser()
		parser.parse(tmpl)
		self.parsed = parser.items
		
	def render(self, force=False):
		if force or self.changed:
			self._outlist = []
			code = "\n".join(self.walk())
			namespace = self.variables.copy()
			
			exec code in namespace
			self.output = "".join(self._outlist)
			
			self.changed = False
			
		return self.output
		
	__str__ = render
		
	def __setitem__(self, attr, value):
		self.variables[attr] = value
		self.changed = True
		
	@staticmethod
	def from_file(filename):
		try:
			f = file(filename)
			return Template(f.read())
		except IOError, e:
			raise TemplateNotFoundError("filename", msg=e)
		
	@staticmethod
	def from_parsed(parsed):
		template = Template("")
		template.parsed = parsed  # XXX: parsed is copied shallowly
		return template
		
	def copy(self, onlyparsed=False):
		if onlyparsed:
			return self.from_parsed(self.parsed)
		else:
			template = self.from_parsed(self.parsed)
			template.variables = self.variables.copy()
			
			return template	
		
	def handle_header(self, value, level):
		output = "%s%s:" % ("\t"*level,value)
		self.levels.append(level)
		return (level + 1,output)
		
	def handle_end(self, value, level):
		return (self.levels.pop(),"")
		
	def handle_chain(self, value, level):
		newlevel = self.levels.pop()
		self.levels.append(newlevel)
		output = "%s%s:" % ("\t"*newlevel,value)
		return (newlevel + 1,output)
		
	def handle_oneliner(self, value, level):
		if value.startswith("#"):
			return (level,"")
			
		return (level,"%s%s" % ("\t"*level,value))
		
	def handle_text(self, value, level):
		def q(i, v):
			if i % 2:
				return "%s" % v
			else:
				return "'''%s'''" % v
				
		values = [q(*iv) for iv in enumerate(self.variable.split(value))]
		output = "%s__emit(%s)" % ("\t"*level,", ".join(values))
		return (level,output)
		
	def walk(self):
		level = 0
		output = []
		for handler, value in self.parsed:
			level, out = getattr(self, "handle_%s" % handler)(value, level)
			if out:
				output.append(out)
				
		return output


if __name__ == "__main__":
	test = r"""
<html>
	<body>
		<table>
		{% for name, age in people.iteritems()
			<tr>
				<td>$name</td><td>$age</td>
				{% if age > 60
					<td>old</td>
				%} elif age > 30 {%
					<td>not old</td>
				%} elif age > 20 {%
					<td>young</td>
				%} elif age > 15 {%
					<td>teen</td>
				%} elif age > 10 {%
					<td>very young</td>
				%} elif age > 5 {%
					<td>kiddo</td>
				%} else {%
					<td>baby</td>
				%}
			</tr>
		%}
		</table>
		{% 'oneliner\n' %}
	</body>
</html>
"""
	template = Template(test)
	template["people"] = dict(gugu=24, aliyanki=13)
	print str(template)

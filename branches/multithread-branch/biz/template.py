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


class Parser:
	beginline = re.compile(r"(.*(\{%){0})(\{%)(.*)")
	endline = re.compile(r"^\s*(%\})(.*)")
	onelinerline = re.compile(r"(.*)(\{%){0}(\{%)(.*)(%\}){0}(%\})(.*)")
	chainedline = re.compile(r"^\s*(%\})(.*)(\{%)\s*$")
	
	TEXT, HEADER, END, CHAIN, ONELINER = \
		"text", "header", "end", "chain", "oneliner"
	
	def __init__(self):
		self.handlers = [("chain",self.chainedline),
						("oneliner",self.onelinerline),
						("header",self.beginline),
						("end",self.endline)]
						
		self.items = []

	def handle_header(self, groups):
		text, none_, symb, code = groups		
		if text:
			self.items.append((self.TEXT,text))
		
		self.items.append((self.HEADER,code.strip()))
		
	def handle_end(self, groups):
		symb, text = groups		
		self.items.append((self.END,None))
		if text:
			self.items.append((self.TEXT,"%s\n" % text))
			
	def handle_chain(self, groups):
		symb1, code, symb2 = groups		
		self.items.append((self.CHAIN,code.strip()))
		
	def handle_oneliner(self, groups):
		print "oneliner", groups
		btext, none1, symb1, code, none2, symb2, atext = groups
		
		if btext:
			self.items.append((self.TEXT,btext))
		
		self.items.append((self.ONELINER,code.strip()))
		
		if atext:
			self.items.append((self.TEXT,"%s\n" % atext))
		
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
				self.handle_text(r"%s\n" % line)


class Template:
	variable = re.compile(r"\$[{]?(\w+)[}]?")

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
		f = file(filename)
		try:
			return Template(f.read())
		finally:
			f.close()
		
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
			
		return (level,"%s__emit(%s)" % ("\t"*level,value))
		
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
	test = """
<html>
<body>
{% for name, age in people.iteritems()
<tr>
<td>${name}</td>
before text {% if age > 10
<td>${age}</td>
ifififi
%} elif age > 5 {%
<td>young</td>
elelel
%} else {%
<td>very young</td>
%} after text
</tr>
%}
before oneliner {% 2*2 %} after oneliner
${age}
{% # this is supposed to be a comment %}
</body>
</html>
"""

	template = Template(test)
	template["people"] = dict(yuce=27, gugu=24)
	print str(template)

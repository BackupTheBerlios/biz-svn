# -*- coding: utf-8 -*-
# catalog.py -- Biz translation

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

import os.path
from cStringIO import StringIO

_DEFAULT = "DEFAULT"


class Translator(object):
	__slots__ = "catalog","domain"
	
	def __init__(self, catalog, domain):
		self.catalog = catalog
		self.domain = domain
		
	def __call__(self, trstr):
		return self.catalog.consult(trstr, domain=self.domain)


class _Noop(object):
	__slots__ = "catalog","domain","trstr"
	
	def __init__(self, catalog, domain, trstr):
		self.catalog = catalog
		self.domain = domain
		self.trstr = trstr
		
	def __str__(self):
		return self.catalog.consult(self.trstr, domain=self.domain)
		
		
class NoopTranslator(object):
	__slots__ = "catalog","domain"
	
	def __init__(self, catalog, domain):
		self.catalog = catalog
		self.domain = domain
		
	def __call__(self, trstr):
		return _Noop(self.catalog, self.domain, trstr)
		

class Context(object):
	__slots__ = "catalog","lang","default_lang","domain"
	
	def __init__(self, catalog, lang, default_lang, domain):
		self.catalog = catalog
		self.lang = lang
		self.default_lang = lang
		self.domain = domain
		
	def set_language(self, lang):
		self.lang = lang
		
	def get_translator(self):
		return Translator(self, self.domain)
		
	def get_noop_translator(self):
		return NoopTranslator(self, self.domain)

	def consult(self, text, lang=None, domain=None):
		lang = lang or self.lang or self.default_lang
		domain = domain or self.domain or _DEFAULT
		
		try:
			return self.catalog[lang].get((text,domain), text)
		except KeyError:
			try:
				return self.catalog[self.default_lang].get((text,domain), text)
				self.lang = self.default_lang
			except KeyError:
				return text


class LanguageCatalog:
	def __init__(self, lang=None, domain=None):
		self.catalog = {}
		self.domain = domain
		self.lang = lang
		self.default_lang = lang
		
	def addtext(self, lang, text):
		self.load(lang, StringIO(text))
	
	@classmethod
	def open(cls, catalog_dir, langs, lang=None, domain=None):
		assert isinstance(langs, list)
		
		cat = LanguageCatalog(lang, domain)		
		for lang in langs:
			f = file(os.path.join(catalog_dir, "%s.bic" % lang))
			cat.load(lang, f)
			f.close()
				
		return cat
		
	def load(self, lang, fileobj):
		lang = lang or self.lang
		self.catalog[lang] = {}
		catalog = self.catalog[lang]
		orig_str = ""
		trans_str = ""
		options = dict(domain=_DEFAULT, charset="utf-8")
		
		for line in fileobj:
			line = line.strip()
			
			if line.startswith("#"):
				continue
				
			elif not line:
				if orig_str and trans_str:
					catalog[(orig_str,options["domain"])] = trans_str
					orig_str = trans_str = ""					
				
			elif line.startswith(">"):
				if orig_str:
					raise Exception("Original string should be followed by the translation")
				orig_str = line[1:].strip()
					
			elif line.startswith("<"):
				if trans_str:
					raise Exception("Translated string should be followed by newline")
				trans_str = line[1:].strip()
					
			else:
				try:
					key, value = line.split(":", 1)
				except ValueError:
					raise Exception("Invalid string: %s" % line)
					
				options[key.strip().lower()] = value.strip() or _DEFAULT
		
		if orig_str and trans_str:
			catalog[(orig_str,options["domain"])] = trans_str
			orig_str = trans_str = ""
			
	def get_context(self, lang=None, default_lang=None, domain=None):
		return Context(self.catalog, lang or self.lang or self.default_lang,
				default_lang or self.default_lang, domain or self.domain)

def test():
	text_tr_TR = """Author: Someone
Language: tr_TR
Charset: utf-8

Domain: comp

> Hello, World!
< Merhaba Dünya!

> buffer
< arabellek

Domain:

> buffer
< yastık"""

	text_en_EN = """Author: Someone
Language: en_EN
Charset: utf-8

Domain: comp

> Hello, World!
< Hello, World!

> buffer
< buffer

Domain:

> buffer
< buffer"""

	text_de_DE = """Author: Someone
Language: de_DE
Charset: utf-8

Domain: comp

> Hello, World!
< Hallo, Welt!
"""

	lc = LanguageCatalog(domain="comp")
	lc.addtext("tr_TR", text_tr_TR)
	lc.addtext("en_EN", text_en_EN)
	lc.addtext("de_DE", text_de_DE)
	print lc.catalog
	
	context = lc.get_context()
	N_ = context.get_noop_translator()
	mystr = N_("Hello, World!")
	context.set_language("tr_TR")
	print mystr
	context.set_language("en_EN")
	print mystr
	context.set_language("de_DE")
	print mystr
	
	
	
if __name__ == "__main__":
	test()

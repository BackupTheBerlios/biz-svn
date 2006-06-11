# utility.py

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

class Struct:
	def __init__(self, **kwargs):
		self.__dict__.update(**kwargs)
		self.__contains__ = self.__dict__.__contains__
		self._get = self.__dict__.get		
		self._has_key = self.__dict__.has_key

	def __setitem__(self, key, value):
		self.__dict__[key] = value

	def __getitem__(self, key):
		return self.__dict__[key]

	def _getdict(self):
		return dict([(k,v) for 
				k,v in self.__dict__.iteritems() if not k.startswith("_")])

	def _getlist(self):
		return [(k,v) for 
				k,v in self.__dict__.iteritems() if not k.startswith("_")]
				


class Heads(Struct):
## 	def _getdict(self):
## 		return dict([(k.replace("_", "-"),str(v)) for
## 				k,v in self.__dict__.iteritems() if not k.startswith("_")])

	def _getlist(self):
		r = []
		for k, v in self.__dict__.iteritems():
			if k.startswith("_"):
				continue
				
			k = k.replace("_", "-")
			if isinstance(v, list):
				r.extend([(k,str(vx)) for vx in v])
			else:
				r.append((k,str(v)))
				
		return r

class Cookie:
	def __init__(self, cookiename, value, **kwargs):
		self.name = cookiename
		self.value = value
		# XXX: find a better name for ``values``
		self.values = kwargs
		
	def __getitem__(self, key):
		return self.values[key]
		
	def __setitem__(self, key, value):
		self.values[key] = value
		
	def __repr__(self):
		return "%s=%s; %s" % (self.name,str(self.value),
			" ".join(["%s=%s;" % (k.capitalize(),str(v))
				for k,v in self.values.iteritems()]))
			

class CookieJar:
	def __init__(self, cookiestring=""):
		self.cookies = self._process_cookiestring(cookiestring)
		self.__contains__ = self.cookies.__contains__
		
	def _process_cookiestring(self, cookiestring):
		def g(kv):
			return (kv[0],Cookie(kv[0],kv[1]))
			
		morsels = [g(x.strip().split("=")) for x in cookiestring.split(";") if x]
		return dict(morsels)
		
	def __getitem__(self, key):
		return self.cookies[key]
		
	def __setitem__(self, key, value):
		self.cookies[key] = Cookie(key, value)
		
	def __delitem__(self, key):
		del self.cookies[key]
		
	def add(self, cookiename, value, **kwargs):
		self.cookies[cookiename] = Cookie(cookiename, value, **kwargs)
		
	def modify(self, cookie):
		self.cookies[cookie.name] = cookie
		
	def remove(self, cookiename):
		del self.cookies[cookiename]
		
	def update(self, cookiejar):
		self.cookies.update(cookiejar.cookies)
		
	def getlist(self):
		return [str(v) for v in self.cookies.values()]
			
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
	def _getdict(self):
		return dict([(k.replace("_", "-"),str(v)) for
				k,v in self.__dict__.iteritems() if not k.startswith("_")])

	def _getlist(self):
			return [(k.replace("_", "-"),str(v)) for
				k,v in self.__dict__.iteritems() if not k.startswith("_")]


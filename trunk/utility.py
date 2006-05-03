# utility.py


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


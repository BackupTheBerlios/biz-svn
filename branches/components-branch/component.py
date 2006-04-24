# component.py -- Biz components


class Component:
	requires = []
	accepts = []
	provides = []

	def __init__(self):
		self.resources = []

		self.requires = set(self.requires)
		self.accepts = set(self.accepts)
		self.properties = {}

		self.provides = set(self.provides)
		self.providing = {}

	def prepare(self):
		"""prepare the component

		* Call this after you fulfilled the requirements.
		* Extend this.
		"""
		assert not self.requiresany(), "Component has unfulfilled requirements:\n%s" % \
									", ".join(list(self.requires.difference(set(self.properties))))

	def collect(self):
		for r in self.resources:
			self.collectfrom(r)

	def collectfrom(self, other):
		other.prepare()
		props = list(self.requires.union(self.accepts).intersection(other.provides))
		for p in props:
			self.properties[p] = other.providing[p]

	def collectfromonly(self, other, only):
		other.prepare()
		props = list((self.requires).union(self.accepts).intersection(set(only)).intersection(other.provides))
		for p in props:
			self.properties[p] = other.providing[p]

	def provideto(self, other):
		self.prepare()
		props = list(other.requires.union(other.accepts).intersection(self.provides))
		for p in props:
			other.propertis[p] = self.providing[p]

	def requiresany(self):
		return self.requires.difference(set(self.properties))

	def providesall(self):
		return not self.provides.difference(set(self.providing))


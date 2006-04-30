# router.py


class Router:
	def __init__(self):
		self.handlers = {}

	def register(self, name, handler):
		self.handlers[name] = handler

	def __call__(self, name, args):
		if self.handlers.has_key(name):
			m = self.handlers[name]
			m.run(args)
			return m.get()
			return True
		else:
			return None



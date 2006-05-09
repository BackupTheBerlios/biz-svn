# connection.py


# TODO: write the unittests !!
# TODO: write docstrings !!

# TODO: Change this to gettext !
def _(s):
	return s


class PropertyException(Exception):
	pass


class Source:
	def __init__(self, conn, alias=""):
		self.conn = conn
		self.alias = alias
		# set this to allowed properties in inherited classes
		self._allowedprops = []
		self.clients = []
		self.fields = {}
		
	def _modify(self, **kwargs):
		d = {}
		for prop, value in kwargs.iteritems():
			# check if property is allowed
			if prop in self._allowedprops:
				d[prop] = value
			else:
				raise PropertyException(_("%s is not a valid property") % prop)

		self.__dict__.update(d)
		
	def register(self, client):
		self.clients.append(client)
		
	def collect(self):
		for cli in self.clients:
			self.fields[cli.field] = cli.value
			

class DatabaseSource(Source):
	def __init__(self, conn, alias="", **kwargs):
		Source.__init__(self, conn, alias)
		self._allowedprops = ["selectstr", "insertstr", "updatestr", "deletestr"]
		self._modify(**kwargs)
		
		self.db = self.conn.db
		self.cursor = self.db.cursor()
		
	def select(self):
		self.collect()
		cu = self.cursor
		cu.execute(self.selectstr % self.fields)
		return cu.fetchall()

	def insert(self):
		self.collect()
		cu = self.cursor
		cu.execute(self.insertstr % self.fields)
		self.db.commit()
		
	def update(self):
		self.collect()
		cu = self.cursor
		cu.execute(self.updatestr % self.fields)
		self.db.commit()
		
	def delete(self):
		self.collect()
		cu = self.cursor
		cu.execute(self.deletestr % self.fields)
		self.db.commit()


class Connection:
	def new_source(self, alias="", **kwargs):
		pass
		
	def close(self):
		pass
		

class DatabaseConnection(Connection):
	def __init__(self, **kwargs):
		self.db = None
		##self.sources = {}
		
	def new_source(self, alias="", **kwargs):
		##if alias:
		##    if alias in self.sources:
		##        # return the source by alias, ignore select et al.
		##        return self.sources[alias]
		##    else:
		##        ds = DatabaseSource(self, alias, **kwargs)
		##        self.sources[alias] = ds
		##        return ds
		##else:
		##    return DatabaseSource(self, "", **kwargs)
		return DatabaseSource(self, alias, **kwargs)
				
	def close(self):
		if self.db:
			self.db.close()


# -*- coding: utf-8 -*-

import shelve
import md5

__all__ = ["UserManager"]


class UserManager:
	"""Hold user information.
	
	Each entry in the shelve has:	
	* [0] confuscated password.
	* [1] ``set`` of groups user belongs to (default: [users, $username])
	"""
	
	def __init__(self, filename):
		self.s = shelve.open(filename)
	
	@staticmethod
	def confuscate(username, password):
		"""Confuscate the ``password`` using the ``username``.
		"""
		m = md5.new(username)
		m.update(password)
		
		return m.digest()
	
	
	def add(self, username, password):
		"""Add user ``username`` with ``password`` to shelve.
		"""
		if self.s.has_key(username):
			return False
		
##		self.s[username] = self.confuscate(username, password)
		self.s[username] = (self.confuscate(username, password),set(["users", username]))
		
		return True
		
	def addgroup(self, username, groups):
		"""Add ``groups`` to the groups of the user.
		
		* ``groups`` is an iterable.
		"""
		s = self.s
		try:
			# Doing update longway. Because: see Python manual 3.17.2
			gs = s[username][1]
			gs.update(groups)
			s[username] = (s[username][0],gs)
		except KeyError:
			return False
		
		return True
		
	def ingroup(self, username, group):
		"""Return ``True`` if user is a member of ``group``.
		"""
		try:
			return group in self.s[username][1]
		except KeyError:
			return False
			
	def groups(self, username):
		"""Return groups of the user ``username``.
		"""
		try:
			return self.s[username][1]
		except KeyError:
			return False
		
	def remove(self, username):
		"""Remove user ``username`` from shelve.
		"""
		try:
			del self.s[username]
		except KeyError:
			return False
			
		return True
		
	def check(self, username, password):
		"""Check if the ``password`` is right for user ``username``.
		"""
		try:
			c = self.s[username][0]
			return c == self.confuscate(username, password)
		except KeyError:
			return False
			
	def close(self):
		self.s.close()
	
def test():
	import os
	TEST_FILENAME = "TEST_USERMAN.db"
	
	try:
		os.remove(TEST_FILENAME)
	except OSError:
		pass
		
	userman = UserManager(TEST_FILENAME)
	
	userman.add("bunny", "ax123bcd")
	assert userman.check("bunny", "ax123bcd")
	assert not userman.check("bunny", "xxx")
	assert userman.ingroup("bunny", "bunny")
	assert userman.ingroup("bunny", "users")
	
	userman.addgroup("bunny", ["admins"])
	assert userman.ingroup("bunny", "admins")
	assert not userman.ingroup("bunny", "locs")
	
	userman.remove("bunny")
	assert not userman.check("bunny", "ax123bcd")
	print "** Test Passed **"
	
if __name__ == "__main__":
	test()

# session.py

from Cookie import SimpleCookie

from utility import Struct
from biz.uuid import uuid_time

SESSION_ID = "sid"


class SessionError(Exception):
	pass

class SessionManager:
	def __init__(self):
		self.sessions = {}

	def get_session(self, cookies):
		if not SESSION_ID in cookies:  # XXX
			return (cookies,self.new_session())
		else:
			sid = cookies[SESSION_ID].value
			del cookies[SESSION_ID]
			try:
				return (cookies,self.sessions[sid])
			except KeyError:
				raise SessionError("invalid session")

	def new_session(self):
			session = Session(self, self._new_id())
			self.sessions[session.sid] = session
			return session

	def update(self, session):
		try:
			if session.sid:
				self.sessions[session.sid] = session
			else:  # revoke
				del self.session[session.sid]
		except KeyError:
			print "session update error"  # TODO: Do some logging here

	def revoke(self, sid):
		##try:
			##self.sessions[sid] = None
		del self.sessions[sid]
		#except KeyError:
		#    pass

	def _new_id(self):
		return str(uuid_time())


class Session:
	def __init__(self, sessionman, sid):
		self.sessionman = sessionman
		self.sid = sid
		self.sidcookie = SimpleCookie("%s=%s" % (SESSION_ID,self.sid))
		self.data = Struct()

	def close(self):
		if self.sid:
			self.sidcookie = SimpleCookie("%s=" % SESSION_ID)
			self.sessionman.revoke(self.sid)

	def __setitem__(self, key, value):
		self.data[key] = value

	def __getitem__(self, key):
		return self.data[key]




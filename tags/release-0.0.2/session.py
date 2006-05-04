# session.py

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

import time
from Cookie import SimpleCookie

from utility import Struct
from biz.uuid import uuid_time

SESSION_ID = "sid"


class SessionError(Exception):
	pass

class SessionTimeout(SessionError):
	pass

class SessionExpire(SessionError):
	pass


class SessionManager:
	def __init__(self, timeout=0, expiretime=0):
		self.sessions = {}
		self.timeout = timeout  # max time of user inactivity (sec)
		self.expiretime = expiretime  # expire time after session creation (sec)

	def get_session(self, cookies):
		if not SESSION_ID in cookies:  # XXX
			return (cookies,self.new_session())
		else:
			sid = cookies[SESSION_ID].value
			del cookies[SESSION_ID]
			try:
				s = self.sessions[sid]
				t = time.time()

				if self.timeout:
					if t > s.accesstime + self.timeout:
						s.close()
						raise SessionTimeout("session timeout")

				if self.expiretime:
					if t > s.creationtime + self.expiretime:
						s.close()
						raise SessionExpire("session expired")

				s.accesstime = t
				return (cookies,s)
			except KeyError:
				raise SessionError("invalid session")

	def new_session(self):
		new_id = self._new_id()
		while new_id in self.sessions.keys():  # !!!: If too many sessions open, may lock the system
			new_id = self._new_id()

		session = Session(self, new_id)
		self.sessions[new_id] = session

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
		self.creationtime = time.time()
		self.accesstime = self.creationtime

	def close(self):
		if self.sid:
			self.sidcookie = SimpleCookie("%s=" % SESSION_ID)
			self.sessionman.revoke(self.sid)

	def __setitem__(self, key, value):
		self.data[key] = value

	def __getitem__(self, key):
		return self.data[key]




#/usr/bin/env python2.5
#----------------------------
# Datastore models for user & signup
#----------------------------

from base64 import b64encode as b64
from hashlib import md5, sha256
from random import randint
from time import time

from google.appengine.ext import db

from util.aetycoon import MorphedProperty, AutomorphicProperty

N_SALT = 8             # length of the password salt

def salt_n_hash(password, salt=None):
	"""
	Generate a salt and return in base64 encoding the hash of the
	password with the salt and the character '$' prepended to it.
	"""
	salt = salt or b64( ''.join(chr(randint(0, 0xff)) for _ in range(N_SALT)) )
	return salt + '$' + b64( sha256(salt+password.encode("ascii")).digest() )

class User(db.Model):
	"""
	Constructor arg:
		key_name = nickname
	"""
	nickname = db.StringProperty(required=True)
	email = db.EmailProperty(required=True)
	pwd = MorphedProperty(salt_n_hash, required=True)
	suspended = db.BooleanProperty(default=True)
	
	@classmethod
	def authenticate(klass, nickname, password):
		"""Return an User() entity instance if password is correct or None"""
		user = klass.get_by_key_name(nickname)
		if user:
			n_salt = user.pwd.index('$')
			if user.pwd == salt_n_hash( password, salt=user.pwd[:n_salt] ):
				return user
	
	def __eq__(self, other):
		return self.nickname == other.nickname

class UserSignup(db.Model):
	user = db.ReferenceProperty(User, required=True)
	date = db.DateProperty(auto_now_add=True)
	
	@AutomorphicProperty
	def code(self):
		return md5( self.user.nickname + repr(time()) ).hexdigest()

from utils.base import Handler
from google.appengine.ext import db

from hashlib import md5
import re

class User(db.Model):
	username = db.StringProperty(required = True)
	hashValue = db.StringProperty(required = True)
	email = db.StringProperty()


class Register(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.render('SignUpFront.html', default_user = "",
								user_comment =  "",
								default_pass =  "",
								pass_comment =  "",
								default_vrf = "",
								vrf_comment = "",
								default_email = "",
								email_comment = ""
								)
	
	def post(self):
		user = self.request.get("username")
		pswd = self.request.get("password")
		vrf = self.request.get("verify")
		email = self.request.get("email")

		val_data = self._validate_data(user, pswd, vrf, email)

		# condition
		if (val_data[0] and val_data[1] and val_data[2] and val_data[3]):
			#1. Check validity of data on registration form
			#2. If valid, start registeration process
			#3. While registering him check if the name is already taken or not (look into db)
			#4. If name not taken, register him and set a cookie


			self.register(user, pswd, vrf, email)
		
		else:
			default_user = user
			user_comment = "" if val_data[0] else "That's not a valid username." 
			default_pass = ""
			pass_comment = "" if val_data[1] else "That wasn't a valid password."
			default_vrf = ""
			if val_data[1]:
				vrf_comment = "" if val_data[2] else "Your passwords didn't match."
			else:
				vrf_comment = ""

			default_email = email
			email_comment = "" if val_data[3] else "That's not a valid email"

			self.render('SignUpFront.html', default_user =  default_user, 
									user_comment =  user_comment, 
									default_pass =  default_pass,
									pass_comment =  pass_comment,
									default_vrf = default_vrf,
									vrf_comment = vrf_comment,
									default_email = default_email,
									email_comment = email_comment
									)

	def _validate_data(self, user, pswd, vrf, email):
		res = []
		USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
		res.append(USER_RE.match(user))

		PASS_RE = re.compile(r"^.{3,20}$")
		res.append(PASS_RE.match(vrf))

		if res[1]: 
			res.append(pswd == vrf)
		else:
			res.append(False)

		if email != "":
			EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
			res.append(EMAIL_RE.match(email))
		else:
			res.append(True)

		res = [bool(i) for i in res]
		return res

	def register(self, user, pswd, vrf, email):
		# First check if name taken or not
		if User.all().filter('username =', user).get():

			self.render('SignUpFront.html', default_user =  user, 
									user_comment =  "Name already taken", 
									default_pass =  "",
									pass_comment =  "",
									default_vrf = "",
									vrf_comment = "",
									default_email = email,
									email_comment = ""
									)
		else:
			# Name is available along with the all validity tests passed
	
			#1. Store the data
			_key = db.Key.from_path('users', 'default') # basically a dummy entity, will help in orgranising data
			acc = User(parent = _key, username = user, hashValue = Register.genHashVal(user, pswd), email = email)
			acc.put()

			#2. Set a cookie for the new user
			self.response.headers.add_header('Set-Cookie',
											'user_id = %s; Path=/' %(Register.genCookieVal(acc.key().id())))

			#3. Redirect it to success page
			self.redirect('/blog/welcome')

	@classmethod
	def genHashVal(cls, user, pswd):
		secret = '8ahdxbz80g428u7ujjf1'
		return md5(user + pswd + secret).hexdigest()
	
	@classmethod
	def genCookieVal(cls, user_id):
		secret = '4hc9b13j9ly4kex3ieyr'
		return "%s|%s" %(user_id, md5(str(user_id) + secret).hexdigest())

	@classmethod
	def validate_cookie(cls, keyID, hashValue):
		return Register.genCookieVal(keyID).split('|')[1] == hashValue


class SignUpSuccess(Handler):
	def get(self):
		#1. Recover key id
		cookieVal = self.request.cookies.get('user_id')
		if cookieVal:
			keyID, hashValue = cookieVal.split('|')
			#2. Validate the cookie
			if keyID and Register.validate_cookie(keyID, hashValue):
				#3. Generate key
				key = db.Key.from_path('User', int(keyID), parent = db.Key.from_path('users', 'default'))

				#4. Exract username
				username = db.get(key).username
				self.response.write("Welcome, " + str(username) + '!')
			else:
				self.redirect('/blog/signup')

		else:
			self.redirect('/blog/signup')


class Login(Handler):
	def get(self):
		self.render('LoginForm.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		#1. Check if username and passwords exits
		entity = User.all().filter('username =', username).get()

		if entity and self._validate_password(username, password, entity.hashValue):
			#2. Set cookie
			self.response.headers.add_header('Set-Cookie',
											 'user_id = %s; Path = /' %(Register.genCookieVal(entity.key().id())))
			#3. Redirect to welcome page
			self.redirect('/blog/welcome')
		else:
			#4. Redirect to same login page
			self.render('LoginForm.html', error = "Invalid login")

	
	def _validate_password(self, username, password, hashValue):
		return Register.genHashVal(username, password) == hashValue

		
class Logout(Handler):
	def get(self):
		#1. Clear cookie value from the browser
		self.response.headers.add_header('Set-Cookie',
										'user_id =%s; Path= /' %(''))
		#2. Redirect to signup page
		self.redirect('/blog/signup')









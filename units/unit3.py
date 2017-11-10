from utils.base import Handler
from google.appengine.ext import db

import json

class Blog(db.Model):
	"""This is a db instance of one blog """
	title = db.StringProperty(required =  True)  #Limits length to 500 characters
	blog = db.TextProperty(required =  True)
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now = True)


class FrontPage(Handler):
	""" Simply renders all the blogs"""
	def render_front(self):
		blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 10")
		self.render('BlogFront.html', posts = blogs)

	def get(self):		
		self.render_front()


class FormPage(Handler):
	""" Dedicated page to post your blogs """
	def get(self):
		self.render('BlogForm.html')
	
	def post(self):
		# take the code and then redirect to id page
		title = self.request.get('subject')
		blog = self.request.get('content')

		# error handling
		if title and blog:
			# also set parent for every entity created here
			_key = db.Key.from_path('blogs', 'default') # basically a dummy entity, will help in orgranising data
			p = Blog(parent = _key, title =  title, blog = blog)
			p.put()
			id_key = p.key().id()

			# extract whole key for reterival and key numeric identifier for redirect url


			# now redirect it to the self post for the given identifier
			self.redirect('/blog/' + str(id_key))

		else:
			error = "Either Subject or Content Section is empty"
			self.render('BlogForm.html', error = error, title = title, blog = blog)


class PostPage(Handler):
	""" Renders the successfully submitted blog entity """
	def get(self, id_key):
		# generate key
		key = db.Key.from_path('Blog', int(id_key), parent = db.Key.from_path('blogs', 'default'))
		entity = db.get(key)

		if not entity:
			self.write("Error 404, Object doesn't exist")
			return

		title = entity.title
		created = entity.created
		content = entity.blog.replace('\n', '<br>')

		self.render('BlogPost.html', content = content, title = title, created = created)
		

class PostPageJson(Handler):
	def get(self, jid_key):
		#1. Extract id_key from here
		id_key = jid_key
		print id_key
		#2. Gerate key
		key = db.Key.from_path('Blog', int(id_key), parent = db.Key.from_path('blogs', 'default'))

		#3. Extract entity from db
		entity = db.get(key)

		#4. Make json object
		pobj = {}
		pobj['content'] = entity.blog
		pobj['title'] = entity.title

		jobj = json.dumps(pobj)

		#5. Render
		self.response.headers['Content-Type'] = 'application/json'
		self.write(jobj)


class FrontPageJson(Handler):
	def get(self):		
		res = []
		#1. Fetch all the blog entries
		blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 10")
		#2. Store all dictionary objects in a list
		for blog in blogs:
			temp = {}
			temp['title'] = blog.title
			temp['content'] = blog.blog
			res.append(temp)

		#3. Render json list
		res = json.dumps(res)
		self.response.headers['Content-Type'] = 'application/json'
		self.write(res)











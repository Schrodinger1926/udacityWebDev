import os
import re
import webapp2
import jinja2


template_dir = os.path.join(os.path.dirname(__file__), 'templates')

from home import MainPage

from units.unit3 import FormPage
from units.unit3 import FrontPage
from units.unit3 import PostPage
from units.unit3 import FrontPageJson
from units.unit3 import PostPageJson
from units.unit4 import Register
from units.unit4 import SignUpSuccess
from units.unit4 import Login
from units.unit4 import Logout


app = webapp2.WSGIApplication([
	('/', MainPage),
	('/blog/signup', Register),
	('/blog/welcome', SignUpSuccess),
	('/blog/login', Login),
	('/blog/logout', Logout),
	('/blog', FrontPage),
	('/blog/.json', FrontPageJson),
	('/blog/newpost', FormPage),
	('/blog/([0-9]+)', PostPage),
	('/blog/([0-9]+).json', PostPageJson)
	], debug = True)
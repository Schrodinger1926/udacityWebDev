import webapp2
import jinja2


from main import template_dir



class Handler(webapp2.RequestHandler):
	"""
	Base class handler
	"""

	# environment is common for all
	jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)

	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **params):
		t = Handler.jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
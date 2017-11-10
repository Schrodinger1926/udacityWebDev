from utils.base import Handler

class MainPage(Handler):
	def get(self):
		self.render('front.html')
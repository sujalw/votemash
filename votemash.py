import cgi
import datetime
import urllib
import webapp2
import jinja2
import os
import random

#from data import *
from Search import *
from Edit import *
from Vote import *
from Result import *

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MainPage(webapp2.RequestHandler):

	def post(self):
		if users.get_current_user():
			user_name = users.get_current_user().nickname()
			url = users.create_logout_url('/')
			url_linktext = 'Logout'

			# get what action is to be taken
			task_name = getField(self, 'task_name')
			if task_name:
				if task_name == 'edit':
					self.redirect('/edit')

				elif task_name == 'vote':
					authorNames = set([])
					
					categories = db.GqlQuery("SELECT * FROM Category")

					for category in categories:
						authorNames.add(category.author)

					template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'authorNames': authorNames,
						'back_url': self.request.url,
						'home_url': '/',
					}

					template = jinja_environment.get_template('vote.html')
					self.response.out.write(template.render(template_values))

				elif task_name == 'results':
				
					categories = db.GqlQuery("SELECT * FROM Category")

					authorNames = set([])
					for category in categories:
						authorNames.add(category.author)

					template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'authorNames': authorNames,
						'back_url': self.request.url,
						'home_url': '/',
					}
									
					template = jinja_environment.get_template('result.html')
					self.response.out.write(template.render(template_values))
					
				elif task_name == 'search':
				
					template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'back_url': self.request.url,
						'home_url': '/',
					}
									
					template = jinja_environment.get_template('search.html')
					self.response.out.write(template.render(template_values))

			else:
				template_values = {
					'user_name': user_name,
					'url': url,
					'url_linktext': url_linktext,
					'home_url': '/',
				}

				template = jinja_environment.get_template('index.html')
				self.response.out.write(template.render(template_values))
				
	def get(self):
		if users.get_current_user():
			self.post()
		else:
			self.redirect(users.create_login_url(self.request.uri))
				
app = webapp2.WSGIApplication([('/', MainPage),
								('/votemash', MainPage),
								('/editcategory', Edit),
								('/edit', Edit),
								('/vote', Vote),
								('/result', Result),
								('/search', Search)], 
								debug=True)

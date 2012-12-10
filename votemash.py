import cgi
import datetime
import urllib
import webapp2
import jinja2
import os

#from data import *

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Item(db.Model):
	name = db.StringProperty()
	votesFor = db.IntegerProperty()
	votesAgainst = db.IntegerProperty()

class Category(db.Model):
	name = db.StringProperty()
	author = db.StringProperty()

class MainPage(webapp2.RequestHandler):

	def post(self):
		if users.get_current_user():
			user_name = users.get_current_user().nickname()
			url = users.create_logout_url(self.request.url)
			url_linktext = 'Logout'

			# get what action is to be taken
			task = self.request.get('task')
			if task:
				if task == 'edit':
					self.redirect('/edit')
					'''
					template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'task_name': 'edit the category'
					}

					template = jinja_environment.get_template('edit.html')
					self.response.out.write(template.render(template_values))
					'''
				elif task == 'vote':
					template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'task_name': 'caste a vote'
					}

					template = jinja_environment.get_template('vote.html')
					self.response.out.write(template.render(template_values))

				elif task == 'results':
					template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'task_name': 'see the leaderboard'
					}

					template = jinja_environment.get_template('result.html')
					self.response.out.write(template.render(template_values))

			else:
				template_values = {
					'user_name': user_name,
					'url': url,
					'url_linktext': url_linktext,
				}

				template = jinja_environment.get_template('index.html')
				self.response.out.write(template.render(template_values))
				
	def get(self):
		if users.get_current_user():
			self.post()
		else:
			self.redirect(users.create_login_url(self.request.uri))

class Edit(webapp2.RequestHandler):
	def get(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url(self.request.url)
		url_linktext = 'Logout'
		'''
		categories = db.GqlQuery(	"SELECT * "
									"FROM Category "
									"WHERE ANCESTOR IS :1 ",
									category_key(user_name))

		template_values = {
			'user_name': user_name,
			'url': url,
			'url_linktext': url_linktext,
			'categories': categories,
		}

		template = jinja_environment.get_template('edit.html')
		self.response.out.write(template.render(template_values))
		'''
		self.display(user_name, url, url_linktext)

	def post(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url(self.request.url)
		url_linktext = 'Logout'

		category_name = cgi.escape(self.request.get('category_name')).strip()
		if category_name:
			if self.is_present(user_name, category_name) == False:
				category = Category(parent=category_key(user_name))
				category.author = user_name
				category.name = category_name
				category.put()

				self.display(user_name, url, url_linktext)

			else:				
				self.display(user_name, url, url_linktext, 'Category "' + category_name + '" already created')
				self.response.out.write('category ' + category_name + ' is already present')
		else:
			self.response.out.write('no category name given')

	def is_present(self, user_name, category_name):
		categories = db.GqlQuery(	"SELECT * "
									"FROM Category "
									"WHERE ANCESTOR IS :1 ",
									category_key(user_name))

		for cat in categories:
			if cat.name == category_name:
				return True

		return False
		
		
	def display(self, user_name, url, url_linktext, error_msg=None):
		categories = db.GqlQuery(	"SELECT * "
									"FROM Category "
									"WHERE ANCESTOR IS :1 ",
									category_key(user_name))

		template_values = {
			'user_name': user_name,
			'url': url,
			'url_linktext': url_linktext,
			'categories': categories,
			'error_msg': error_msg
		}

		template = jinja_environment.get_template('edit.html')
		self.response.out.write(template.render(template_values))

def category_key(user_name=None):
	return db.Key.from_path('Author', user_name)

app = webapp2.WSGIApplication([('/', MainPage),
								('/votemash', MainPage),
								('/edit', Edit)], 
								debug=True)

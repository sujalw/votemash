import cgi
import datetime
import urllib
import webapp2
import jinja2
import os
import random

from Data import *

from google.appengine.ext import db
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Result(webapp2.RequestHandler):

	def get(self):
		self.response.out.write('in get')

	def post(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url('/')
		url_linktext = 'Logout'
						
		selected_user = self.request.get('author_name')
		task_name = self.request.get('task_name')
		
		if task_name == "choose_category":
			# display categories of the selected user
			categories = db.GqlQuery(	"SELECT * "
										"FROM Category "
										"WHERE ANCESTOR IS :1 ",
										category_key(selected_user))

			template_values = {
				'user_name': user_name,
				'selected_user': selected_user,
				'url': url,
				'url_linktext': url_linktext,
				'categories': categories,
				'back_url':self.request.url,
			}
		
			template = jinja_environment.get_template('choosecategoryresults.html')
			self.response.out.write(template.render(template_values))
			
		elif task_name == "view_leaderboard":
			category_name = self.request.get('category_name')
			selected_user = self.request.get('selected_user')
			
			# get all items ordered by their votesFor
			items = db.GqlQuery("SELECT * "
													"FROM Item "
													"WHERE ANCESTOR IS :1 "
													"ORDER BY votesFor DESC",
													item_key(user_name, category_name))
				
			template_values = {
				'user_name': user_name,
				'category_name': category_name,
				'selected_user': selected_user,
				'url': url,
				'url_linktext': url_linktext,
				'items': items,
				'back_url': self.request.url,
			}
		
			template = jinja_environment.get_template('leaderboard.html')
			self.response.out.write(template.render(template_values))

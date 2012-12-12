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

class Search(webapp2.RequestHandler):

	def get(self):
		self.response.out.write('in get of search')

	def post(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url('/')
		url_linktext = 'Logout'
						
		task_name = self.request.get('task_name')
		
		if task_name == "search_items":
			keywords = self.request.get('keywords')
			
			authors = set([])
						
			# get all users of the system
			categories = Category.all()
			for category in categories:
				authors.add(category.author)
			
			# loop through all authors
			for author in authors:
				# search for all categories by current user
				categories = db.GqlQuery(	"SELECT * "
																	"FROM Category "
																	"WHERE ANCESTOR IS :1 ",
																	category_key(author))
																	
				# dict to store search results
				searchResults = {}
								
				for category in categories:
					# search for all items in each category
					items = db.GqlQuery(	"SELECT * "
																"FROM Item "
																"WHERE ANCESTOR IS :1 ",
																item_key(user_name, category.name))
														
					for item in items:
						if keywords in item.name:
							resultInfo = {}
							resultInfo['category'] = category.name
							resultInfo['author'] = author
							
							searchResults[item.name] = resultInfo
						
			
			#
			template_values = {
				'user_name': user_name,
				'keywords': keywords,
				'url': url,
				'url_linktext': url_linktext,
				'searchResults': searchResults,
				'back_url': '/',
				'home_url': '/',
			}
		
			template = jinja_environment.get_template('search.html')
			self.response.out.write(template.render(template_values))

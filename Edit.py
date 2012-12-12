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

class Edit(webapp2.RequestHandler):
	
	def get(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url('/')
		url_linktext = 'Logout'

		self.displayCategories(user_name, url, url_linktext)

	def post(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url('/')
		url_linktext = 'Logout'

		task_name = getField(self, 'task_name')

		if task_name == 'edit_category':
			# display all items in this category and display option to add new items
			category_name = self.getField('category_name')

			# get all items from this category
			items = db.GqlQuery(	"SELECT * "
									"FROM Item "
									"WHERE ANCESTOR IS :1 ",
									item_key(user_name, category_name))

			self.displayItems(user_name, category_name, url, url_linktext)

		elif task_name == 'create_item':
			category_name = getField(self, 'category_name')
			item_name = getField(self, 'item_name')
			
			if item_name:
				# create a new item under current category, if it is not already present
				if self.item_present(user_name, category_name, item_name) == False:
					item = Item(parent=item_key(user_name, category_name))
					item.name = item_name
					item.votesFor = 0
					item.votesAgainst = 0
					item.put()

					self.displayItems(user_name, category_name, url, url_linktext)

				else:
					# display error message
					self.displayItems(user_name, category_name, url, url_linktext, 'Item "' + item_name + '" has already been created')

			else:
				# display error message
				self.displayItems(user_name, category_name, url, url_linktext, 'Item name cannot be blank')

		elif task_name == 'create_category':
			category_name = getField(self, 'category_name')
			if category_name:
				# create a new category, if it is not already created
				if self.is_present(user_name, category_name) == False:
					category = Category(parent=category_key(user_name))
					category.author = user_name
					category.name = category_name
					category.put()

					self.displayCategories(user_name, url, url_linktext)

				else:
					# display error message
					self.displayCategories(user_name, url, url_linktext, 'Category "' + category_name + '" has already been created')
			else:
				# display error message
				self.displayCategories(user_name, url, url_linktext, 'Category name cannot be blank')

		elif task_name == 'delete_category':
			category_name = getField(self, 'delete_category_name')
			if category_name:				
				categories = Category.all()
				for category in categories:
					if category.name == category_name:
						category.delete()
						break

				self.displayCategories(user_name, url, url_linktext)
				
		elif task_name == 'delete_item':
			item_name = getField(self, 'delete_item_name')
			category_name = getField(self, 'category_name')
			if item_name:				
				items = Item.all()
				for item in items:
					if item.name == item_name:
						item.delete()
						break

				self.displayItems(user_name, category_name, url, url_linktext)

	def is_present(self, user_name, category_name):
		categories = db.GqlQuery(	"SELECT * "
									"FROM Category "
									"WHERE ANCESTOR IS :1 ",
									category_key(user_name))

		for category in categories:
			if category.name == category_name:
				return True

		return False
		
	def item_present(self, user_name, category_name, item_name):
		items = db.GqlQuery("SELECT * "
							"FROM Item "
							"WHERE ANCESTOR IS :1 ",
							item_key(user_name, category_name))

		for item in items:
			if item.name == item_name:
				return True

		return False
		
	def displayCategories(self, user_name, url, url_linktext, error_msg=None):
		categories = db.GqlQuery(	"SELECT * "
									"FROM Category "
									"WHERE ANCESTOR IS :1 ",
									category_key(user_name))

		template_values = {
			'user_name': user_name,
			'url': url,
			'url_linktext': url_linktext,
			'categories': categories,
			'error_msg': error_msg,
			'back_url': self.request.url,
			'home_url': '/',
		}

		template = jinja_environment.get_template('edit.html')
		self.response.out.write(template.render(template_values))

	def displayItems(self, user_name, category_name, url, url_linktext, error_msg=None):
		items = db.GqlQuery(	"SELECT * "
								"FROM Item "
								"WHERE ANCESTOR IS :1 ",
								item_key(user_name, category_name))

		template_values = {
			'user_name': user_name,
			'category_name': category_name,
			'url': url,
			'url_linktext': url_linktext,
			'items': items,
			'error_msg': error_msg,
			'back_url': self.request.url,
			'home_url': '/',
		}

		template = jinja_environment.get_template('editcategory.html')
		self.response.out.write(template.render(template_values))

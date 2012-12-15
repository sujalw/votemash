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
			category_name = getField(self, 'category_name')

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
			
			if isEmpty(category_name):
				self.displayCategories(user_name, url, url_linktext, 'Category name cannot be blank')
			
			else:
				if category_name:
					# create a new category, if it is not already created
					if is_present(self, user_name, category_name) == False:
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
				
		elif task_name == 'rename_category':
			category_name = getField(self, 'category_name')
			category_name_new = getField(self, 'category_name_new')
			
			if isEmpty(category_name_new):
				self.displayItems(user_name, category_name, url, url_linktext, "", "name cannot be blank")
				
			else:			
				# create a new category, if it is not already created
				if is_present(self, user_name, category_name_new) == False:			
					categories = db.GqlQuery(	"SELECT * "
																		"FROM Category "
																		"WHERE ANCESTOR IS :1 ",
																		category_key(user_name))

					# transfer all items from old category to the new one
					for category in categories:
						if category.name == category_name:
					
							# create a new category with new name
							category_new = Category(parent=category_key(category.author))
							category_new.author = ''.join(category.author)
							category_new.name = ''.join(category_name_new)
							category_new.put()
					
							# get all items in the category with old name
							items = db.GqlQuery(	"SELECT * "
																		"FROM Item "
																		"WHERE ANCESTOR IS :1 ",
																		item_key(category.author, category.name))

							# transfer all items from old category in the new category
							for item in items:
								item_new = Item(parent=item_key(category_new.author, category_new.name))
								item_new.name = ''.join(item.name)
								item_new.votesFor = item.votesFor
								item_new.votesAgainst = item.votesAgainst
								item_new.put()
						
								item.delete()
												
							# remove the old category
							category.delete()
					
							break
					
					self.displayItems(user_name, category_name_new, url, url_linktext, "", "Category renamed successfully.")
					
				else:
					# display error message
						self.displayCategories(user_name, url, url_linktext, 'Error: Category "' + category_name_new + '" has already been created')
				
		elif task_name == 'rename_item':
			category_name = getField(self, 'category_name')
			item_name_old = getField(self, 'item_name_old')
			item_name_new = getField(self, 'item_name_new')
			
			if isEmpty(item_name_new):
				self.displayItems(user_name, category_name, url, url_linktext, "", "", "Item name cannot be blank")
			
			else:
				# get all items
				items = db.GqlQuery(	"SELECT * "
															"FROM Item "
															"WHERE ANCESTOR IS :1 ",
															item_key(user_name, category_name))
														
				# find item to rename
				for item in items:
					if item.name == item_name_old:
						createNewItem(item_name_new, category_name, user_name, item.votesFor, item.votesAgainst)
					
						# delete old item
						item.delete()
					
						break
					
				self.displayItems(user_name, category_name, url, url_linktext, "", "", "Item renamed successfully.")
					

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
				
		elif task_name == 'export':
			#self.response.out.write("export")
			#self.response.headers['Content-Type'] = 'text/csv'
			#self.response.headers['Content-Disposition'] = "attachment; filename=fname.csv"
			#self.response.out.write(','.join(['a', 'cool', 'test']))
			
			# display users to choose one for exporting data
			authorNames = set([])
					
			categories = db.GqlQuery("SELECT * FROM Category")

			for category in categories:
				authorNames.add(category.author)
				
			error_msg = None
			if len(authorNames) <= 1:
				error_msg = "There are no other users in the system"
				
			template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'authorNames': authorNames,
						'error_msg': error_msg,
						'back_url': self.request.url,
						'home_url': '/',
					}

			template = jinja_environment.get_template('selectuser.html')
			self.response.out.write(template.render(template_values))
			
		elif task_name == "choose_categories":
			selected_user = getField(self, 'selected_user')
			
			# display categories to choose to export
			categories = db.GqlQuery(	"SELECT * "
										"FROM Category "
										"WHERE ANCESTOR IS :1 ",
										category_key(selected_user))

			template_values = {
				'user_name': user_name,
				'url': url,
				'url_linktext': url_linktext,
				'selected_user': selected_user,
				'categories': categories,
				'back_url': self.request.url,
				'home_url': '/',
			}
		
			template = jinja_environment.get_template('choosecategories.html')
			self.response.out.write(template.render(template_values))
			
		elif task_name == "export_categories":
			#self.response.out.write("in export categories<br/>")
			selected_user = getField(self, 'selected_user')			
			selectedCategory = getField(self, 'category_name')			
			exportToXml(self, selected_user, selectedCategory)
			
		elif task_name == 'import':
			template_values = {
				'user_name': user_name,
				'url': url,
				'url_linktext': url_linktext,
				'back_url': self.request.url,
				'home_url': '/',
			}

			template = jinja_environment.get_template('import.html')
			self.response.out.write(template.render(template_values))
			
		elif task_name == 'import_category':
			category_file = getField(self, 'imported_file')
			back_url = getField(self, 'back_url')
			importCategory(self, user_name, category_file, url, url_linktext, back_url)
	
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
									
		no_category_error_msg = None
		if categories.count() == 0:
			no_category_error_msg = "No categories created by you"

		template_values = {
			'user_name': user_name,
			'url': url,
			'url_linktext': url_linktext,
			'categories': categories,
			'no_category_error_msg': no_category_error_msg,
			'error_msg': error_msg,
			'back_url': self.request.url,
			'home_url': '/',
		}

		template = jinja_environment.get_template('edit.html')
		self.response.out.write(template.render(template_values))

	def displayItems(self, user_name, category_name, url, url_linktext, error_msg=None, status_msg=None, status_msg_item=None):
		items = db.GqlQuery(	"SELECT * "
								"FROM Item "
								"WHERE ANCESTOR IS :1 ",
								item_key(user_name, category_name))

		no_items_error_msg = None
		if items.count() == 0:
			no_items_error_msg = "No items in the current category"
			
		template_values = {
			'user_name': user_name,
			'category_name': category_name,
			'url': url,
			'url_linktext': url_linktext,
			'items': items,
			'error_msg': error_msg,
			'status_msg': status_msg,
			'status_msg_item': status_msg_item,
			'no_items_error_msg': no_items_error_msg,
			'back_url': self.request.url,
			'home_url': '/',
		}

		template = jinja_environment.get_template('editcategory.html')
		self.response.out.write(template.render(template_values))

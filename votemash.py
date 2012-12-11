import cgi
import datetime
import urllib
import webapp2
import jinja2
import os
import random

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
			url = users.create_logout_url('/')
			url_linktext = 'Logout'

			# get what action is to be taken
			task = self.request.get('task')
			if task:
				if task == 'edit':
					self.redirect('/edit')

				elif task == 'vote':
					authorNames = set([])
					
					categories = db.GqlQuery("SELECT * FROM Category")

					for category in categories:
						authorNames.add(category.author)

					template_values = {
						'user_name': user_name,
						'url': url,
						'url_linktext': url_linktext,
						'authorNames': authorNames
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

#########################  Editing  ###############################

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

		task_name = self.request.get('task_name')

		if task_name == 'edit_category':
			# display all items in this category and display option to add new items
			category_name = cgi.escape(self.request.get('category_name')).strip()

			# get all items from this category
			items = db.GqlQuery(	"SELECT * "
									"FROM Item "
									"WHERE ANCESTOR IS :1 ",
									item_key(user_name, category_name))

			self.displayItems(user_name, category_name, url, url_linktext)

		elif task_name == 'create_item':
			category_name = cgi.escape(self.request.get('category_name')).strip()
			item_name = cgi.escape(self.request.get('item_name')).strip()
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
			category_name = cgi.escape(self.request.get('category_name')).strip()
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
			category_name = cgi.escape(self.request.get('delete_category_name')).strip()
			if category_name:				
				categories = Category.all()
				for category in categories:
					if category.name == category_name:
						category.delete()
						break

				self.displayCategories(user_name, url, url_linktext)
				
		elif task_name == 'delete_item':
			item_name = cgi.escape(self.request.get('delete_item_name')).strip()
			category_name = cgi.escape(self.request.get('category_name')).strip()
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
			'error_msg': error_msg
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
			'error_msg': error_msg
		}

		template = jinja_environment.get_template('editcategory.html')
		self.response.out.write(template.render(template_values))

#########################  Voting  ###############################

class Vote(webapp2.RequestHandler):

	def get(self):
		self.response.out.write('in get')

	def post(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url('/')
		url_linktext = 'Logout'
						
		selected_user = self.request.get('author_name')
		
		task_name = self.request.get('task_name')
		#self.response.out.write('task_name = ' + task_name)
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
			}
		
			template = jinja_environment.get_template('choosecategory.html')
			self.response.out.write(template.render(template_values))
			
		elif task_name == "vote_category":
			category_name = self.request.get('category_name')
			selected_user = self.request.get('selected_user')
			
			self.displayItemsToVote(user_name, selected_user, category_name, url, url_linktext)						
			
		elif task_name == "cast_vote":
			selected_user = self.request.get('selected_user')
			category_name = self.request.get('category_name')
			vote = self.request.get('item_to_vote')
			item1 = self.request.get('item1')
			item2 = self.request.get('item2')
			
			self.displayItemsToVote(user_name, selected_user, category_name, url, url_linktext, vote, item1, item2)
			'''
			items = db.GqlQuery("SELECT * "
													"FROM Item "
													"WHERE ANCESTOR IS :1 ",
													item_key(selected_user, category_name))
			
			# update votes for item 1
			item1_votes = 0
			for item in items:
				if item.name == item1:
					if vote == "1":
						item.votesFor = item.votesFor + 1						
					else:
						item.votesAgainst = item.votesAgainst + 1
						
					item1_votes = item.votesFor						
					item.put()
					
					break
					
			# update votes for item 2
			item2_votes = 0
			for item in items:
				if item.name == item2:
					if vote == "2":
						item.votesFor = item.votesFor + 1
					else:
						item.votesAgainst = item.votesAgainst + 1
						
					item2_votes = item.votesFor						
					item.put()
					
					break
					
			template_values = {			
				'user_name': user_name,
				'selected_user': selected_user,
				'category_name': category_name,
				'url': url,
				'url_linktext': url_linktext,		
				'votedFor': item1 if vote=="1" else item2,
				'votedAgainst': item2 if vote=="1" else item1,
				'votedFor_votes': item1_votes if vote=="1" else item2_votes,
				'votedAgainst_votes': item2_votes if vote=="1" else item1_votes,
			}
		
			template = jinja_environment.get_template('voteitem.html')
			self.response.out.write(template.render(template_values))'''
			
	def displayItemsToVote(self, user_name, selected_user, category_name, url, url_linktext, vote=None, item1=None, item2=None):
		# select 2 random items in this category. Display error message in case of not enough items, i.e <2
			items = db.GqlQuery("SELECT * "
													"FROM Item "
													"WHERE ANCESTOR IS :1 ",
													item_key(user_name, category_name))
													
			if items.count() >= 2:
				index1 = random.randint(0, items.count()-1)
				index2 = index1
			
				while index2 == index1:
					index2 = random.randint(0, items.count()-1)
				
				itemsToVote = []
				itemsToVote.append(items[index1].name)
				itemsToVote.append(items[index2].name)

				template_values = {
					'user_name': user_name,
					'selected_user': selected_user,
					'category_name': category_name,
					'url': url,
					'url_linktext': url_linktext,
					'itemsToVote': itemsToVote,
				}
				
				if vote:
					# update votes for item 1
					item1_votes = 0
					for item in items:
						if item.name == item1:
							if vote == "1":
								item.votesFor = item.votesFor + 1						
							else:
								item.votesAgainst = item.votesAgainst + 1
						
							item1_votes = item.votesFor						
							item.put()
					
							break
					
					# update votes for item 2
					item2_votes = 0
					for item in items:
						if item.name == item2:
							if vote == "2":
								item.votesFor = item.votesFor + 1
							else:
								item.votesAgainst = item.votesAgainst + 1
						
							item2_votes = item.votesFor						
							item.put()
					
							break
							
					# add voted info to be displayed on the page 		
					template_values['votedFor'] = item1 if vote=="1" else item2
					template_values['votedAgainst'] = item2 if vote=="1" else item1
					template_values['votedFor_votes'] = item1_votes if vote=="1" else item2_votes
					template_values['votedAgainst_votes'] = item2_votes if vote=="1" else item1_votes
					
				template = jinja_environment.get_template('voteitem.html')
				self.response.out.write(template.render(template_values))
				
			else:
				template_values = {			
					'user_name': user_name,
					'selected_user': selected_user,
					'category_name': category_name,
					'url': url,
					'url_linktext': url_linktext,		
					'error_msg': "The category does not have enough items to vote",
				}
		
				template = jinja_environment.get_template('voteitem.html')
				self.response.out.write(template.render(template_values))
				
#########################  Misc  ###############################

def category_key(user_name=None):
	return db.Key.from_path('Author', user_name)

def item_key(user_name=None, category_name=None):
	return db.Key.from_path('Author', user_name, 'Category', category_name)

app = webapp2.WSGIApplication([('/', MainPage),
								('/votemash', MainPage),
								('/editcategory', Edit),
								('/edit', Edit),
								('/vote', Vote)], 
								debug=True)

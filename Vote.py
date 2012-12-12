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

class Vote(webapp2.RequestHandler):

	def get(self):
		self.response.out.write('in get')

	def post(self):
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url('/')
		url_linktext = 'Logout'
						
		selected_user = getField(self, 'author_name')		
		task_name = getField(self, 'task_name')

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
				'back_url': self.request.url,
				'home_url': '/',
			}
		
			template = jinja_environment.get_template('choosecategory.html')
			self.response.out.write(template.render(template_values))
			
		elif task_name == "vote_category":
			category_name = getField(self, 'category_name')
			selected_user = getField(self, 'selected_user')
			
			self.displayItemsToVote(user_name, selected_user, category_name, url, url_linktext)						
			
		elif task_name == "cast_vote":
			selected_user = getField(self, 'selected_user')
			category_name = getField(self, 'category_name')
			vote = getField(self, 'item_to_vote')
			item1 = getField(self, 'item1')
			item2 = getField(self, 'item2')
			
			self.displayItemsToVote(user_name, selected_user, category_name, url, url_linktext, vote, item1, item2)
						
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
					'back_url': self.request.url,
					'home_url': '/',
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
					'home_url': '/',
				}
		
				template = jinja_environment.get_template('voteitem.html')
				self.response.out.write(template.render(template_values))

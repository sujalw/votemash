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

class Search(webapp2.RequestHandler):

	def get(self):
		self.response.out.write('in get of search')

	def post(self):
		self.response.out.write('in post of search')
		user_name = users.get_current_user().nickname()
		url = users.create_logout_url('/')
		url_linktext = 'Logout'
						
		task_name = self.request.get('task_name')

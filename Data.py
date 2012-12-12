import cgi

from google.appengine.ext import db

class Item(db.Model):
	name = db.StringProperty()
	votesFor = db.IntegerProperty()
	votesAgainst = db.IntegerProperty()

class Category(db.Model):
	name = db.StringProperty()
	author = db.StringProperty()
	
def category_key(user_name=None):
	return db.Key.from_path('Author', user_name)

def item_key(user_name=None, category_name=None):
	return db.Key.from_path('Author', user_name, 'Category', category_name)
	
def getField(self, fieldName):
	return cgi.escape(self.request.get(fieldName)).strip()

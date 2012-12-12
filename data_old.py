from google.appengine.ext import db

class Item(db.Model):
	name = db.StringProperty()
	votesFor = db.IntegerProperty()
	votesAgainst = db.IntegerProperty()

class Category(db.Model):
	name = db.StringProperty()
	author = db.StringProperty()

import cgi
import urllib
import codecs
import jinja2
import os

from google.appengine.ext import db
from google.appengine.api import users
from xml.etree.ElementTree import Element, SubElement, tostring, XML, fromstring
import xml.etree.ElementTree as ET
from cStringIO import StringIO
from xml.parsers import expat
from xml.dom.minidom import parseString
import urllib2
import xml.dom.minidom
import re

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

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
	
def getFields(self, fieldName):
	return self.request.get_all(fieldName)

def exportToXml(self, user_name, selectedCategory):
	#self.response.out.write("<br/> inside export xml")
	self.response.headers['Content-Type'] = 'text/xml'
	file_name = selectedCategory.replace(' ', '_')
	self.response.headers['Content-Disposition'] = "attachment; filename=" + str(file_name) + ".xml"
	#self.response.out.write(','.join(['a', 'cool', 'test']))
	
	# create xml file
	
	# get all items in the chosen category
	items = db.GqlQuery(	"SELECT * "
												"FROM Item "
												"WHERE ANCESTOR IS :1 ",
												item_key(user_name, selectedCategory))
												
	root = Element('CATEGORY')
	categoryName = SubElement(root, 'NAME')
	categoryName.text = selectedCategory
	
	# create intermediate nodes for each item
	for item in items:
		itemTag = SubElement(root, 'ITEM')
		itemNameTag = SubElement(itemTag, 'NAME')
		itemNameTag.text = item.name
		
	self.response.out.write(tostring(root, encoding="us-ascii", method="xml"))	

def importCategory(self, user_name, category_file):
	# parse the category file
	#self.response.out.write(category_file)
	#tree = ET.parse(codecs.open(StringIO(cgi.escape(category_file))), encoding="UTF-8")
	#codecs.open("file.xml", encoding="UTF-8")
	
	x = category_file
	dom = xml.dom.minidom.parseString(x)
	#tree = ET.XML(category_file, parser=None)
	#dom = parseString(category_file.encode('utf-8'))
	#dom = xml.dom.minidom.parse(StringIO(category_file.encode('utf-8')))
	
	#xml_contents = fromstring(cgi.escape(category_file))	
	#root = xml_contents.getroot()
	#self.response.out.write(root)
	
	#self.response.out.write(category_file)
	#element = ET.XML(category_file.encode('utf-8'))
	
	'''
	category = Category(parent=category_key(user_name))
	category.author = user_name
	category.name = category_name
	category.put()
	'''

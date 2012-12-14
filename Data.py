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
	
def getUniqueKey(author, category_name, item_name):
	return db.Key.from_path('Author', author, 'Category', category_name, 'Item', item_name)
	
def getField(self, fieldName):
	return cgi.escape(self.request.get(fieldName)).strip()
	
def getFields(self, fieldName):
	return self.request.get_all(fieldName)
	
def is_present(self, user_name, category_name):
	categories = db.GqlQuery(	"SELECT * "
														"FROM Category "
														"WHERE ANCESTOR IS :1 ",
														category_key(user_name))

	for category in categories:
		if category.name.upper() == category_name.upper():
			return True

	return False
	
def createNewItem(item_name, category_name, user_name, votes_for, votes_against):
	item_new = Item(parent=item_key(user_name, category_name))
	item_new.name = item_name
	item_new.votesFor = votes_for
	item_new.votesAgainst = votes_against
	item_new.put()
	
def isEmpty(txt):
	return txt.strip() == ""

def exportToXml(self, user_name, selectedCategory):
	#self.response.out.write("<br/> inside export xml")
	self.response.headers['Content-Type'] = 'text/xml'
	file_name = selectedCategory.replace(' ', '_')
	self.response.headers['Content-Disposition'] = "attachment; filename=" + str(file_name) + ".xml"
	
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

def importCategory(self, user_name, category_file, url, url_linktext, back_url):
	# parse the category file
	#self.response.out.write(category_file)
	#tree = ET.parse(codecs.open(StringIO(cgi.escape(category_file))), encoding="UTF-8")
	#codecs.open("file.xml", encoding="UTF-8")
	
	#self.response.out.write("<br/> in import category")
	#x = category_file
	
	#self.response.out.write(x)
	#dom = xml.dom.minidom.parseString(x)
	x = "<CATEGORY><NAME>Operating Systems</NAME><ITEM><NAME>Linux</NAME></ITEM><ITEM><NAME>Windows 8</NAME></ITEM><ITEM><NAME>Mac OSX</NAME></ITEM><ITEM><NAME>Solaris</NAME></ITEM></CATEGORY>"
	
	#x = "    "
	
	
	
	# validate whether the xml file is a valid one and according to the desired format and tag names
	if isEmpty(x)==False and isValidXML(x):	
	
		dom = xml.dom.minidom.parseString(x)
		#tree = ET.XML(category_file, parser=None)
		#dom = parseString(category_file.encode('utf-8'))
		#dom = xml.dom.minidom.parse(StringIO(category_file.encode('utf-8')))
	
		#xml_contents = fromstring(cgi.escape(category_file))	
		#root = xml_contents.getroot()
		#self.response.out.write(root)
	
		#self.response.out.write(category_file)
		#element = ET.XML(category_file.encode('utf-8'))
		
		error_msg = None
	
		# parse xml file
		if x == "":
			error_msg = "XML file is blank"
		else:
			root = fromstring(x)
						
			categoryName = root.findall('NAME')[0].text
			#self.response.out.write("<br/>category = " + categoryName)
			
			# check whether the category with the same name is already present
			if is_present(self, user_name, categoryName) == False:
				# create a new category with new name
				category_new = Category(parent=category_key(user_name))
				category_new.author = user_name
				category_new.name = categoryName
				category_new.put()

				# add items in the newly created category
				for child in root:
					if child.tag.upper() == "ITEM":
						childName = child.findall('NAME')
						createNewItem(item_name=childName[0].text, category_name=category_new.name, user_name=category_new.author, votes_for=0, votes_against=0)
												
			else:
				error_msg = "Conflict: Category '" + categoryName + "' cannot be imported."		
	else:
		error_msg = "Invalid XML file"
		
	template_values = {
				'user_name': user_name,
				'url': url,
				'url_linktext': url_linktext,
				'back_url': back_url,
				'error_msg': error_msg,
				'home_url': '/',
			}

	template = jinja_environment.get_template('import.html')
	self.response.out.write(template.render(template_values))
		
def isValidXML(contents):
	# need to implement this
	
	return True

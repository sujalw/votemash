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
		if category.name.strip().upper() == category_name.strip().upper():
			return True

	return False
	
def is_present_item(self, itemsList, itemName_test):
	for itemName in itemsList:
		if itemName.strip().upper() == itemName_test.strip().upper():
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
	
def getItemsFromXML(contents):
	# it assumes that the given contents are valid

	# get only unique items
	itemNames = set([])
	
	dom = xml.dom.minidom.parseString(contents)
	
	# parse xml file		
	root = fromstring(contents)						
	
	# add items in the newly created category
	for child in root:
		if child.tag == "ITEM":
			childName = child.findall('NAME')[0].text
			itemNames.add(childName.strip())
			
	return itemNames

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
		#itemNameTag.votesFor = item.votesFor
		#itemNameTag.votesAgainst = item.votesAgainst
		
	self.response.out.write(tostring(root))	

def importCategory(self, user_name, category_file, url, url_linktext, back_url):

	if category_file == "":
		error_msg = "Error: No file uploaded or blank file"
	else:
		x = self.request.POST.multi['imported_file'].file.read()

		# check whether the xml file is a valid one and according to the desired format and tag names
		status_valid, error_msg = isValidXML(self, x)
		if status_valid:	
			dom = xml.dom.minidom.parseString(x)
	
			# parse xml file		
			root = fromstring(x)						
			categoryName = root.findall('NAME')
			
			categoryName = categoryName[0].text
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
					if child.tag == "ITEM":
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
	
def importCategoryAdvanced(self, user_name, category_file, url, url_linktext, back_url):

	if category_file == "":
		error_msg = "Error: No file uploaded or blank file"
	else:
		x = self.request.POST.multi['imported_file'].file.read()
		x = x.replace('\n', '')

		# check whether the xml file is a valid one and according to the desired format and tag names
		status_valid, error_msg = isValidXML(self, x)
		if status_valid:	
			#dom = xml.dom.minidom.parseString(x)
	
			# parse xml file		
			root = fromstring(x)
			categoryName = root.findall('NAME')
			categoryName = categoryName[0].text.strip()
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
					if child.tag == "ITEM":
						childName = child.findall('NAME')[0].text.strip()
						createNewItem(item_name=childName, category_name=category_new.name, user_name=category_new.author, votes_for=0, votes_against=0)
												
			else:
				#error_msg = "Conflict: Category '" + categoryName + "' cannot be imported."
				
				# remove all items those are already in the category but not in the new imported category
				# reset vote counts of all items present both old and imported categories
				# add all new items
				categories = db.GqlQuery(	"SELECT * "
																	"FROM Category "
																	"WHERE ANCESTOR IS :1 ",
																	category_key(user_name))

				for category in categories:
					if category.name.upper() == categoryName.upper():
						items = db.GqlQuery(	"SELECT * "
																	"FROM Item "
																	"WHERE ANCESTOR IS :1 ",
																	item_key(user_name, categoryName))
																	
						itemNames = getItemsFromXML(x)
																	
						for item in items:
							#if item.name in itemNames:
							if is_present_item(self, itemNames, item.name):
								# retain common items. remove it from itemNames as it is not required further
								itemNames.remove(item.name)
								pass
								
							else:
								# remove items those are not in imported category
								item.delete()
								
						# add all new items in the category
						for itemName in itemNames:
							createNewItem(item_name=itemName, category_name=categoryName, user_name=user_name, votes_for=0, votes_against=0)
						
						break
				
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
		
def isValidXML(self, contents):
	
	if contents==None or contents.strip()=="":
		return False, "Error: Empty XML file"
	
	try:
		root = fromstring(contents)
	except:
		return False, "Error: Invalid XML file"

	category_name_found = False
	if root.tag == "CATEGORY":
		categoryName = root.findall('NAME')
		if len(categoryName) == 1:
			for child in root:
				if child.tag == "ITEM":
					childName = child.findall('NAME')
					if len(childName) == 1:
						pass
					else:
						self.response.out.write("<br/>child with no tag or more than one tags with name='NAME' present")
						return False, "Error: Exactly one <NAME> tag expected for each <ITEM>"
				else:
					if category_name_found == False:
						category_name_found = True
						pass
					else:
						return False, "Error: Invalid tag : '" + child.tag + "'"
		else:
			return False, "Error: Root tag CATEGORY has more than one <NAME> tags"
	else:
		return False, "Error: Invalid root tag : '" + root.tag + "'"
	
	return True, "Category imported successfully"

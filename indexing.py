import os
# from lxml import etree as ET
from mako.template import Template
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

tree = ET.ElementTree(file="/home/russell/Desktop/indexing/jomi.wordpress.2015-06-11.xml")

# #for each article in the xml file
for elem in tree.iterfind('channel/item'):
	# grab title of article
	title = elem.find('title').text
	link = elem.find('link').text
	# find every element with wp:postmeta
	items = elem.findall("{http://wordpress.org/export/1.2/}postmeta")
	for i in items:
		if i.find('{http://wordpress.org/export/1.2/}meta_key').text == "publication_id":
		 	publication_id = i.find('{http://wordpress.org/export/1.2/}meta_value').text
		elif i.find('{http://wordpress.org/export/1.2/}meta_key').text == "hospital_name":
			affiliation = i.find('{http://wordpress.org/export/1.2/}meta_value').text

	# get date of publishing (will have to parse this later into separate values)
	pubdate = elem.find('pubDate').text
	author_username = elem.find('category[@domain="author"]').text

	for i in tree.iterfind('channel/{http://wordpress.org/export/1.2/}author'):
		if i.find('{http://wordpress.org/export/1.2/}author_login').text == author_username:
			 doctor = i.find('{http://wordpress.org/export/1.2/}author_display_name').text

# remaining: 
# link





# 	#gather all of the data data
# 	#import into mako?
# 	#save file with specific name in specific folder


#mytemplate = Template(filename='/home/russell/Desktop/indexing/JOMI-8.xml')
#print(mytemplate.render())	
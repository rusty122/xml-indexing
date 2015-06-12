import os
from jinja2 import Template
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET




tree = ET.ElementTree(file="/home/russell/Desktop/indexing/jomi.wordpress.2015-06-11.xml")
# For each article in the xml file
for elem in tree.iterfind('channel/item'):
	# Grab title of article
	title = elem.find('title').text
	link = elem.find('link').text
	# find every element with wp:postmeta
	items = elem.findall("{http://wordpress.org/export/1.2/}postmeta")
	for i in items:
		if i.find('{http://wordpress.org/export/1.2/}meta_key').text == "production_id":
		 	production_id = i.find('{http://wordpress.org/export/1.2/}meta_value').text
		elif i.find('{http://wordpress.org/export/1.2/}meta_key').text == "hospital_name":
			affiliation = i.find('{http://wordpress.org/export/1.2/}meta_value').text

	# get date of publishing (will have to parse this later into separate values)
	pubdate = elem.find('pubDate').text
	# get the author's JoMI username (findall if multiple auhors?)
	author_username = elem.find('category[@domain="author"]').text

	for i in tree.iterfind('channel/{http://wordpress.org/export/1.2/}author'):
		if i.find('{http://wordpress.org/export/1.2/}author_login').text == author_username:
			 doctor = i.find('{http://wordpress.org/export/1.2/}author_display_name').text
	# for tag in content:
	# 	print tag
	templateLoader = jinja2.FileSystemLoader( searchpath="/" )
	templateEnv = jinja2.Environment( loader=templateLoader )
	template = env.get_template('mytemplate.html')
	TEMPLATE_FILE = "/home/russell/Desktop/indexing/JOMI-8.xml"
	template = templateEnv.get_template( TEMPLATE_FILE )
	templateVars = { "title" : "Test Example",
                	 "description" : "A simple inquiry of function." }
	# needs to have separate name for each article
	file_ = open('article.xml', 'w')
	file_.write( template.render( templateVars ) )
	file_.close()


#gather all of the data data
#import into mako?
#save file with specific name in specific folder





# Notes: 
# The text for both the Main Text and the Procedure Outline would be appropriate.
# print elem.find('{http://purl.org/rss/1.0/modules/content/}encoded').text
# Do not include the citations, comments, disclosures, or statement of consent.
# Each document will need a unique identifier.  In the example, I used
	# “JOMI-“ along with your identifier.  Adding “JOMI-“ before your
	#  article ID will ensure there is no conflict with any other content we index.
# The section headings are not required, but many times they are themselves informative.
# You should provide a URL for linking.
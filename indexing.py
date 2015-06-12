import os
from jinja2 import Template
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET



tree = ET.ElementTree(file="/home/russell/Desktop/indexing/jomi.wordpress.2015-06-11.xml")
# For each article in the xml file
for elem in tree.iterfind('channel/item'):
	# Initialize an empty dictionary that will be appended
	# to hold all of the data that we parse
	data = {}
	# Save the title and link of the article as dictionary entries
	data['title'] = elem.find('title').text
	data['link'] = elem.find('link').text
	# loop through every element in the article with the tag wp:postmeta
	for i in elem.findall("{http://wordpress.org/export/1.2/}postmeta"):
		# If the text in the meta_key tag is "production_id" 
		# save the meta_value tag text in our dictionary as "production_id"
		if i.find('{http://wordpress.org/export/1.2/}meta_key').text == "production_id":
		 	data['production_id'] = i.find('{http://wordpress.org/export/1.2/}meta_value').text
		 i in elem.findall("{http://wordpress.org/export/1.2/}postmeta"):
		# Otherwise, if the text in the meta_key tag is "hospital_name"
		# save the text of meta_value tag in our dictionary as "affiliation"
		elif i.find('{http://wordpress.org/export/1.2/}meta_key').text == "hospital_name":
			data['affiliation'] = i.find('{http://wordpress.org/export/1.2/}meta_value').text

	# Save date of publishing as dictionary entry "pubdate"
	# (will have to parse this into m-d-y values)
	data['pubdate'] = elem.find('pubDate').text
	# get the author's JoMI username (use findall() if multiple authors exist?)
	author_username = elem.find('category[@domain="author"]').text
	# loop through author listings at beginning of xml doc
	for i in tree.iterfind('channel/{http://wordpress.org/export/1.2/}author'):
		if i.find('{http://wordpress.org/export/1.2/}author_login').text == author_username:
			 data['author'] = i.find('{http://wordpress.org/export/1.2/}author_display_name').text

	# content = elem.find('{http://purl.org/rss/1.0/modules/content/}encoded').text
	# for tag in content:
	# 	print tag

	templateLoader = jinja2.FileSystemLoader( searchpath="/" )
	templateEnv = jinja2.Environment( loader=templateLoader )
	# template = env.get_template('mytemplate.html')
	# check documentation for this part
	TEMPLATE_FILE = "/home/russell/Desktop/indexing/JOMI-8.xml"
	template = templateEnv.get_template( TEMPLATE_FILE )
	templateVars = { "title" : "Test Example",
                	 "description" : "A simple inquiry of function." }
	# needs to have separate name for each article
	file_ = open('article.xml', 'w')
	file_.write( template.render( templateVars ) )
	file_.close()


# parse the necessary data into a dictionary
# render an xml file with the dictionary as the argument
# save file with unique name in specific folder





# Notes: 
# The text for both the Main Text and the Procedure Outline would be appropriate.
# Do not include the citations, comments, disclosures, or statement of consent.
# Each document will need a unique identifier.  In the example, I used
	# “JOMI-“ along with your identifier.  Adding “JOMI-“ before your
	#  article ID will ensure there is no conflict with any other content we index.
# The section headings are not required, but many times they are themselves informative.
# You should provide a URL for linking.
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
	print elem.find('title').text
	# find every element with 
	items = elem.findall("{http://wordpress.org/export/1.2/}postmeta")
	for i in items:
		if i.find('{http://wordpress.org/export/1.2/}meta_key').text == "publication_id":
		 	print i.find('{http://wordpress.org/export/1.2/}meta_value').text

# 	#gather all of the data data
# 	#import into mako?
# 	#save file with specific name in specific folder


#mytemplate = Template(filename='/home/russell/Desktop/indexing/JOMI-8.xml')
#print(mytemplate.render())	
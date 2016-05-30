# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
from scrapy.exceptions import DropItem
import os.path
import hashlib

class DatabaseStorage(object):
	#init database connection
	#doc: http://mysql-python.sourceforge.net/MySQLdb.html#functions-and-attributes
	def __init__(self):
		self.conn = MySQLdb.connect(host='db.dbvis.de', port='3306', db='ccolon', user='ccolon', passwd='b3eY7Tep2F7Pg559Vg0W')
		self.cursor = self.conn.cursor()

	#Store item data in DB.
	#If the item is missing required fields, then an error is logged.
	#The item is returned 
    def process_item(self, item, spider):
		
		#First insert the necessary data into the MetaData table, including an automatically generated primary key. 
		try:
			self.cursor.execute("""INSERT INTO MetaData(localPath, modifiedDate, downloadDate, sourceDomain, url, fileName, title) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (item['path'].encode('utf-8'), item['modifiedDate'].encode('utf-8'), item['downloadDate'].encode('utf-8'), item['sourceDomain'].encode('utf-8'), item['url'].encode('utf-8'), item['filename'].encode('utf-8'), item['title'].encode('utf-8')))
			self.conn.commit()
		
		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
		
		#Second insert the necessary data into the Heritage table, and retrieve the previously generated primary key for consistency. 
		try:
			self.cursor.execute("""INSERT INTO Heritage(id, version, ancestor, decendant) VALUES (%u, %u, %u, %u)""", (self.cursor.lastrowid, item[version], item[ancestor], item[decendant])

		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])

        return item
		
class LocalStorage(object):
	#Init the local file including determining path and filename
	def __init__(self):
		path = '/crawler/01-01-1970/cnn.com/'
		hash = hashlib.md5(item['fileName']).hexdigest()
		self.file = open(path + hash, 'w') #w flag overwrites existing data in that file. Handling?
		
	#Save the html and filename to the local storage folder
	def process_item(self, item, spider):
		html = str(item['html']) #python requires strings to write. If html is stored as a string, then this method call can be removed
		self.file.write(html)
		self.file.close()
		
		return item
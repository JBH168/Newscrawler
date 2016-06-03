# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
from scrapy.exceptions import DropItem
import os.path
import hashlib

class Heuristics(object):

	def __init__(self):

	def process_item(self, item, spider):
		return item

class DatabaseStorage(object):

	#init database connection
	#doc: http://mysql-python.sourceforge.net/MySQLdb.html#functions-and-attributes
	def __init__(self):
		self.conn = MySQLdb.connect(host='db.dbvis.de', port='3306', db='ccolon', user='ccolon', passwd='b3eY7Tep2F7Pg559Vg0W')
		self.cursor = self.conn.cursor()

		#Init all necessary DB queries for this pipeline
		compareVersions = ("""SELECT * FROM CurrentVersion WHERE url=item.url""")
		insertCurrent = ("""INSERT INTO CurrentVersion(modifiedDate,downloadDate,sourceDomain,url,hashedName,title,ancestor)""")
		insertArchive = ("""INSERT INTO CurrentVersion(id, modifiedDate,downloadDate,sourceDomain,url,hashedName,title,ancestor)""")
		#TODO
		deleteFromCurrent = ("""""")

	#Store item data in DB.
	#First determine if a version of the article already exists, if so then 'migrate' the older version to the archive table.
	#Second store the new article in the current version table
	def process_item(self, item, spider):

		#Search the CurrentVersion table for a version of the article
		temp = self.cursor.execute(compareVersions)

		#If the article is found in CurrentVerion, then the older version needs to be migrated to the ArchiveVersion table.
		if (temp != 0)
			oldVersion = self.cursor.fetchone()
			#Link the two versions via the ancestor attribute
			item[ancestor] = oldVersion[0] #0 index is the first attribute in the table, namely id.

			#Add the older version to the archive table
			try:
				self.cursor.execute("""insertArchive VALUES (%s, %s, %s, %s, %s, %s, %u)""", (oldVersion[0], oldVersion[1], oldVersion[2], oldVersion[3], oldVersion[4], oldVersion[5], oldVersion[6], oldVersion[7]))
				self.conn.commit()

			except MySQLdb.Error, e:
				print "Error %d: %s" % (e.args[0], e.args[1])

			#Remove the older version from the CurrentVersion table
			#TODO

		#Add the new version of the article to the CurrentVersion table
		try:
			self.cursor.execute("""insertCurrent VALUES (%s, %s, %s, %s, %s, %s, %u)""", (item[modifiedDate], item[downloadDate], item[sourceDomain], item[url], item[hashedName], item[title], item[ancestor]))
			self.conn.commit()

		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])

		#Close DB connection - garbage collection
		self.cursor.close()
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

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import mysql.connector
import datetime
import os.path
import hashlib

class DatabaseStorage(object):

	#init database connection
        #doc: http://mysql-python.sourceforge.net/MySQLdb.html#functions-and-attributes
        def __init__(self):

                #Establish DB connection
                self.conn = mysql.connector.connect(host='db.dbvis.de', port=3306, db='ccolon', user='ccolon', passwd='b3eY7Tep2F7Pg559Vg0W')
                self.cursor = self.conn.cursor(buffered=True)

                #Init all necessary DB queries for this pipeline
                self.compareVersions = ("SELECT * FROM CurrentVersion WHERE url=%s")

                self.insertCurrent = ("INSERT INTO CurrentVersion(localPath,modifiedDate,downloadDate,sourceDomain,url,hashedName,title,ancestor) \
                        VALUES (%(localPath)s, %(modifiedDate)s, %(downloadDate)s, %(sourceDomain)s, %(url)s, %(hashedName)s, %(title)s, %(ancestor)s)")

                self.insertArchive = ("INSERT INTO ArchiveVersion(id,localPath,modifiedDate,downloadDate,sourceDomain,url,hashedName,title,ancestor) \
                        VALUES (%(id)s, %(localPath)s, %(modifiedDate)s, %(downloadDate)s, %(sourceDomain)s, %(url)s, %(hashedName)s, %(title)s, %(ancestor)s)")

                self.deleteFromCurrent = ("DELETE FROM CurrentVersion WHERE url = %s")

        #Store item data in DB.
        #First determine if a version of the article already exists, if so then 'migrate' the older version to the archive table.
        #Second store the new article in the current version table
        def process_item(self, item, spider):

                #Search the CurrentVersion table for a version of the article
                try:
                        temp = self.cursor.execute(self.compareVersions, (item['url'],))

                except mysql.connector.Error as err:
                        print("Something went wrong in query: {}".format(err))


                ## If there is an existing article with the same URL, then move it to the ArchiveVersion table, and delete it from the CurrentVersion table
                oldVersion = self.cursor.fetchone()
                if oldVersion != None:
                        data_test1 = {
                                'id': oldVersion[0],
                                'localPath': oldVersion[1],
                                'modifiedDate': oldVersion[2],
                                'downloadDate': oldVersion[3],
                                'sourceDomain': oldVersion[4],
                                'url': oldVersion[5],
                                'hashedName': oldVersion[6],
                                'title': oldVersion[7],
                                'ancestor': oldVersion[8],
                        }
                        try:
                                self.cursor.execute(self.deleteFromCurrent, (oldVersion[5],))
                                self.conn.commit()
                        except mysql.connector.Error as err:
                                print("Something went wrong in delete: {}".format(err))


                        try:
                                self.cursor.execute(self.insertArchive, data_test1)
                                self.conn.commit()
                        except mysql.connector.Error as err:
                                print("Something went wrong in archive: {}".format(err))

                        # Link the new version with the old
                        item['ancestor'] = oldVersion[8]

		data_test = {
                        'localPath': item['localPath'],
                        'modifiedDate': item['modifiedDate'],
                        'downloadDate': item['downloadDate'],
                        'sourceDomain': item['sourceDomain'],
                        'url': item['url'],
                        'hashedName': item['filename'],
                        'title': item['title'],
                        'ancestor': item['ancestor'],
		}

                #Add the new version of the article to the CurrentVersion table
		try:
                        self.cursor.execute(self.insertCurrent, data_test)
                        self.conn.commit()

                except mysql.connector.Error as err:
                        print("Something went wrong in commit: {}".format(err))

                #Close DB connection - garbage collection
                self.conn.close()
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

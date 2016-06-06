# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import mysql.connector
import datetime
import os.path
#import hashlib
#from newscrawler.helper_classes import savepath_parser 
import logging

################
#
# Handles reponses to HTML responses other than 200 (accept). 
#
################

class HTMLCodeHandling(object):

	def process_item(self, item, spider):
		## For the case where something goes wrong
		if item['spiderResponse'].status != 200:	
			## Item is no longer processed in the pipeline	
			raise DropItem("%s responded with a non-200 response" % item['url'])
		else:
			return item

################
#
# Handles remote storage of the meta data in the DB
#
################

class DatabaseStorage(object):

	#init database connection
        #doc: http://mysql-python.sourceforge.net/MySQLdb.html#functions-and-attributes
        def __init__(self):

                ## Establish DB connection
		## Closing of the connection is handled once the spider closes
                self.conn = mysql.connector.connect(host='db.dbvis.de', port=3306, db='ccolon', user='ccolon', passwd='b3eY7Tep2F7Pg559Vg0W', buffered=True)
                self.cursor = self.conn.cursor()

                ## Init all necessary DB queries for this pipeline
                self.compareVersions = ("SELECT * FROM CurrentVersion WHERE url=%s")

                self.insertCurrent = ("INSERT INTO CurrentVersion(localPath,modifiedDate,downloadDate,sourceDomain,url,hashedName,title,ancestor) \
                        VALUES (%(localPath)s, %(modifiedDate)s, %(downloadDate)s, %(sourceDomain)s, %(url)s, %(hashedName)s, %(title)s, %(ancestor)s)")

                self.insertArchive = ("INSERT INTO ArchiveVersion(id,localPath,modifiedDate,downloadDate,sourceDomain,url,hashedName,title,ancestor) \
                        VALUES (%(id)s, %(localPath)s, %(modifiedDate)s, %(downloadDate)s, %(sourceDomain)s, %(url)s, %(hashedName)s, %(title)s, %(ancestor)s)")

                self.deleteFromCurrent = ("DELETE FROM CurrentVersion WHERE url = %s")

        ## Store item data in DB.
        ## First determine if a version of the article already exists, if so then 'migrate' the older version to the archive table.
        ## Second store the new article in the current version table
        def process_item(self, item, spider):

                ## Search the CurrentVersion table for a version of the article
                try:
                        temp = self.cursor.execute(self.compareVersions, (item['url'],))

                except mysql.connector.Error as err:
                        print("Something went wrong in query: {}".format(err))

                ## If there is an existing article with the same URL, then move it to the ArchiveVersion table, and delete it from the CurrentVersion table
                oldVersion = self.cursor.fetchone()
                if oldVersion != None:
                        oldVersionList = {
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
			## Delete the old version of the article from the CurrentVerion table
                        try:
                                self.cursor.execute(self.deleteFromCurrent, (oldVersion[5],))
                                self.conn.commit()
                        except mysql.connector.Error as err:
                                print("Something went wrong in delete: {}".format(err))

			## Add the old version to the ArchiveVersion table
                        try:
                                self.cursor.execute(self.insertArchive, oldVersionList)
                                self.conn.commit()
                        except mysql.connector.Error as err:
                                print("Something went wrong in archive: {}".format(err))

                        ## Link the new version with the old
                        item['ancestor'] = oldVersion[0]

		currentVersionList = {
                        'localPath': item['localPath'],
                        'modifiedDate': item['modifiedDate'],
                        'downloadDate': item['downloadDate'],
                        'sourceDomain': item['sourceDomain'],
                        'url': item['url'],
                        'hashedName': item['filename'],
                        'title': item['title'],
                        'ancestor': item['ancestor'],
		}

                ## Add the new version of the article to the CurrentVersion table
		try:
                        self.cursor.execute(self.insertCurrent, currentVersionList)
                        self.conn.commit()

                except mysql.connector.Error as err:
                        print("Something went wrong in commit: {}".format(err))

		logging.info("Article inserted into the database.")

                return item

	def close_spider(self, spider):
		## Close DB connection - garbage collection
		self.conn.close()

################
#
# Handles storage of the file on the local system
#
################

class LocalStorage(object):

	#Save the html and filename to the local storage folder
	def process_item(self, item, spider):

        	## Add a log entry confirming the save 
		logging.info("Saving to %s" % item['localPath'])

        	## Ensure path exists
		dir_ = os.path.dirname(item['localPath'])
        	if not os.path.exists(dir_):
            		os.makedirs(dir_)

		## Write raw html to local file system
        	with open(item['localPath'], 'wb') as file_:
            		file_.write(item['spiderResponse'].body)
        		file_.close()
		

		return item

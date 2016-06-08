# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import mysql.connector
import datetime
import os.path
import logging
from ..config import CrawlerConfig

################
#
# Handles reponses to HTML responses other than 200 (accept).
#
################


class HTMLCodeHandling(object):

    def process_item(self, item, spider):
        # For the case where something goes wrong
        if item['spiderResponse'].status != 200:
            # Item is no longer processed in the pipeline
            raise DropItem("%s: Non-200 response" % item['url'])
        else:
            return item

################
#
# Handles remote storage of the meta data in the DB
#
################


class DatabaseStorage(object):

    # init database connection
    def __init__(self):
        self.cfg = CrawlerConfig.get_instance()
        self.db = self.cfg.section("Database")
        # Establish DB connection
        # Closing of the connection is handled once the spider closes
        self.conn = mysql.connector.connect(host=self.db["host"],
                                            port=self.db["port"],
                                            db=self.db["db"],
                                            user=self.db["username"],
                                            passwd=self.db["password"],
                                            buffered=True)
        self.cursor = self.conn.cursor()

        # Init all necessary DB queries for this pipeline
        self.compareVersions = ("SELECT * FROM CurrentVersion WHERE url=%s")

        self.insertCurrent = ("INSERT INTO CurrentVersion(localPath,\
                              modifiedDate,downloadDate,sourceDomain,url,\
                              title, ancestor, descendant, version) VALUES (\
                              %(localPath)s, %(modifiedDate)s,\
                              %(downloadDate)s, %(sourceDomain)s, %(url)s,\
                              %(title)s, %(ancestor)s, %(descendant)s,\
                              %(version)s)")

        self.insertArchive = ("INSERT INTO ArchiveVersion(id, localPath,\
                              modifiedDate, downloadDate, sourceDomain, url,\
                              title, ancestor, descendant, version) VALUES (\
                              %(id)s, %(localPath)s, %(modifiedDate)s,\
                              %(downloadDate)s, %(sourceDomain)s, %(url)s,\
                              %(title)s, %(ancestor)s, %(descendant)s,\
                              %(version)s)")

        self.deleteFromCurrent = ("DELETE FROM CurrentVersion WHERE url = %s")

    # Store item data in DB.
    # First determine if a version of the article already exists,
    #   if so then 'migrate' the older version to the archive table.
    # Second store the new article in the current version table
    def process_item(self, item, spider):

        # Search the CurrentVersion table for a version of the article
        try:
            self.cursor.execute(self.compareVersions, (item['url'],))

        except mysql.connector.Error as err:
            print("Something went wrong in query: {}".format(err))

        # Save the result of the query. Must be done before the add,
        #   otherwise the result will be overwritten in the buffer
        oldVersion = self.cursor.fetchone()

        currentVersionList = {
            'localPath': item['localPath'],
            'modifiedDate': item['modifiedDate'],
            'downloadDate': item['downloadDate'],
            'sourceDomain': item['sourceDomain'],
            'url': item['url'],
            'title': item['title'],
            'ancestor': item['ancestor'],
            'descendant': item['descendant'],
            'version': item['version'], }

        # Add the new version of the article to
        # the CurrentVersion table
        try:
            self.cursor.execute(self.insertCurrent, currentVersionList)
            self.conn.commit()

        except mysql.connector.Error as err:
            print("Something went wrong in commit: {}".format(err))

        logging.info("Article inserted into the database.")

        # Retrieve the auto_id from the new article for the old version's
        #   descendant attribute
        try:
            item['id'] = self.cursor.lastrowid
        except mysql.connector.Error as err:
            print("Something went wrong in id query: {}".format(err))

        print(item['id'])

        # If there is an existing article with the same URL, then move
        #   it to the ArchiveVersion table, and delete it from the
        #   CurrentVersion table
        if oldVersion is not None:
            oldVersionList = {
                'id': oldVersion[0],
                'localPath': oldVersion[1],
                'modifiedDate': oldVersion[2],
                'downloadDate': oldVersion[3],
                'sourceDomain': oldVersion[4],
                'url': oldVersion[5],
                'title': oldVersion[6],
                'ancestor': oldVersion[7],
                'descendant': item['id'],
                'version': oldVersion[9], }

            # Link the new version with the old
            item['ancestor'] = oldVersion[0]

            # Increment version number for the article
            try:
                self.cursor.execute("UPDATE CurrentVersion SET version=%s WHERE id=%s", ((oldVersion[9]+1), item['id'], ))
            except mysql.connector.Error as err:
                print("Something went wrong in version update: {}".format(err))

            # Delete the old version of the article from the
            # CurrentVerion table
            try:
                self.cursor.execute(self.deleteFromCurrent,
                                    (oldVersion[5], ))
                self.conn.commit()
            except mysql.connector.Error as err:
                print("Something went wrong in delete: {}".format(err))

            # Add the old version to the ArchiveVersion table
            try:
                self.cursor.execute(self.insertArchive, oldVersionList)
                self.conn.commit()
            except mysql.connector.Error as err:
                print("Something went wrong in archive: {}".format(err))

        return item

    def close_spider(self, spider):
        # Close DB connection - garbage collection
        self.conn.close()

################
#
# Handles storage of the file on the local system
#
################


class LocalStorage(object):

    # Save the html and filename to the local storage folder
    def process_item(self, item, spider):

        # Add a log entry confirming the save
        logging.info("Saving to %s" % item['localPath'])

        # Ensure path exists
        dir_ = os.path.dirname(item['localPath'])
        if not os.path.exists(dir_):
            os.makedirs(dir_)

        # Write raw html to local file system
        with open(item['localPath'], 'wb') as file_:
            file_.write(item['spiderResponse'].body)
            file_.close()

        return item

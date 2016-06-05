# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class NewscrawlerItem(scrapy.Item):
    # ID of the article in the DB
    id = scrapy.Field()
    # Path of the file on the local filesystem
    localPath = scrapy.Field()
    # When the article was last modified
    modifiedDate = scrapy.Field()
    # When the article was downloaded
    downloadDate = scrapy.Field()
    # Root domain from which the article came
    sourceDomain = scrapy.Field()
    url = scrapy.Field()
    # Hashed filename for local storage
    filename = scrapy.Field()
    # Title of the article
    title = scrapy.Field()
    # Older version of the article in the DB, if exists
    ancestor = scrapy.Field()
    # Raw HTML data for local storage
    html = scrapy.Field()

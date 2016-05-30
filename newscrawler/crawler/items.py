# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class NewscrawlerItem(scrapy.Item):
    title = scrapy.Field() #Title of the article
    modifiedDate = scrapy.Field() #When the article was last modified
    downloadDate = scrapy.Field() #When the article was downloaded
	version = scrapy.Field() #Version of the article in the DB
	ancestor = scrapy.Field() #Older version of the article in the DB, if exists
	decendant = scrapy.Field() #Newer version of the article in the DB, if exists
    sourceDomain = scrapy.Field() #Root domain from which the article came
    url = scrapy.Field() 
	filename = scrapy.Field() #Hashed filename for local storage
	html = scrapy.Field() #Raw HTML data for local storage
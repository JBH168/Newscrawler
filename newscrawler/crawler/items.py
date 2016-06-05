# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    # Title of the article
    title = scrapy.Field()
    # When the article was last modified
    modifiedDate = scrapy.Field()
    # When the article was downloaded
    downloadDate = scrapy.Field()
    # Version of the article in the DB
    version = scrapy.Field()
    # Older version of the article in the DB, if exists
    ancestor = scrapy.Field()
    # Newer version of the article in the DB, if exists
    decendant = scrapy.Field()
    # Root domain from which the article came
    sourceDomain = scrapy.Field()
    url = scrapy.Field()
    # Hashed filename for local storage
    filename = scrapy.Field()
    # Raw HTML data for local storage
    html = scrapy.Field()

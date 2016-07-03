# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    # ID of the article in the DB
    dbID = scrapy.Field()
    # Path of the file on the local filesystem
    localPath = scrapy.Field()
    # absolute path of the file on the local filesystem
    absLocalPath = scrapy.Field()
    # When the article was last modified
    modifiedDate = scrapy.Field()
    # When the article was downloaded
    downloadDate = scrapy.Field()
    # Root domain from which the article came
    sourceDomain = scrapy.Field()
    url = scrapy.Field()
    # Title of the article
    title = scrapy.Field()
    # Older version of the article in the DB, if exists
    ancestor = scrapy.Field()
    # Newer version of the article in the DB, if exists
    descendant = scrapy.Field()
    # Number of versions of the article in the DB
    version = scrapy.Field()
    # Reponse object from crawler
    spiderResponse = scrapy.Field()
    # Title of the article as store in the RSS feed
    rss_title = scrapy.Field()

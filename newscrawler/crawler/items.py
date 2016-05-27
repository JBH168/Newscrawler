# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    title = scrapy.Field()
    timestamp = scrapy.Field()
    url = scrapy.Field()
    html = scrapy.Field()

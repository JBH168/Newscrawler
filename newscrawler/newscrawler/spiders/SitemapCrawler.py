# -*- coding: utf-8 -*-
import scrapy
import os

# own files
from heuristics import is_article
from save import save_webpage


class SitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "sitemap"
    sitemap_urls = ['http://www.der-postillon.com/robots.txt']

    def parse(self, response):
        if is_article(response):
            save_webpage(response)

    def closed(self, reason):
        print reason

        # TODO: write json file
        # with open('data.json', 'wb') as file:
        #     json.dump(data, file, indent=4)
        # file.close()

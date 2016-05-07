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

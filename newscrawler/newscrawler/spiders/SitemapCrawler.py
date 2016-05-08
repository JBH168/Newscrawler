# -*- coding: utf-8 -*-
import scrapy
import os

# own files
from heuristics import is_article
from save import save_webpage


class SitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "sitemap"
    allowed_domains = ["der-postillon.com"]
    sitemap_urls = ['http://www.der-postillon.com/robots.txt']

    def parse(self, response):
        if False:
            # Recursivly crawl all URLs on the current page
            for href in response.css("a::attr('href')"):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse)

        # heuristics
        if is_article(response):
            save_webpage(response)

    def closed(self, reason):
        print reason

        # TODO: write json file
        # with open('data.json', 'wb') as file:
        #     json.dump(data, file, indent=4)
        # file.close()

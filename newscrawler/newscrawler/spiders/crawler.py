# -*- coding: utf-8 -*-
import scrapy


class Crawler(scrapy.Spider):
    name = "crawler"
    allowed_domains = ["zeit.de"]
    start_urls = (
        'http://www.zeit.de/',
    )

    # Recursivly crawles all URLs (on allowed_domains) on the current page
    def parse(self, response):
        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse)

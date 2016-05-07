# -*- coding: utf-8 -*-
import scrapy
import os

# own files
from heuristics import is_article
from save import save_webpage


class Crawler(scrapy.Spider):
    name = "crawler"
    allowed_domains = ["der-postillon.com"]
    start_urls = (
        'http://www.der-postillon.com/',
    )

    # http://doc.scrapy.org/en/latest/topics/spiders.html
    #
    # This method must return an iterable with the first Requests to crawl for
    # this spider. This is the method called by Scrapy when the spider is
    # opened for scraping when no particular URLs are specified.
    #
    # For example, if you need to start by logging in using a POST request,
    # you could do:
    #
    # def start_requests(self):
    #     return [scrapy.FormRequest("http://www.example.com/login",
    #                            formdata={'user': 'john', 'pass': 'secret'},
    #                            callback=self.logged_in)]
    # def logged_in(self, response):
    #     # here you would extract links to follow and return Requests for
    #     # each of them, with another callback
    #     pass

    def parse(self, response):
        # Recursivly crawles all URLs (on allowed_domains) on the current page
        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse)

        # heuristics
        if is_article(response):
            save_webpage(response)

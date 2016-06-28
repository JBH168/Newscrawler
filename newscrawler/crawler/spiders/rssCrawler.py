# -*- coding: utf-8 -*-
import scrapy
import urllib2
from urlparse import urlparse
import re


class rssCrawler(scrapy.Spider):
    name = "rssCrawler"
    ignored_allowed_domains = None
    start_urls = None
    original_url = None

    config = None
    helper = None

    def __init__(self, helper, url, config, ignoreRegex, *args, **kwargs):
        self.config = config
        self.helper = helper

        self.original_url = url

        self.ignored_allowed_domains = [self.helper.url_extractor
                                        .get_allowed_domains(url)]
        self.start_urls = [self.helper.url_extractor.get_start_urls(url)]

        super(rssCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        yield scrapy.Request(self.helper.url_extractor.get_rss_url(response),
                             callback=self.rss_parse)

    def rss_parse(self, response):
        for item in response.xpath('//item'):
            for url in item.xpath('link/text()').extract():
                yield scrapy.Request(url, lambda resp: self.article_parse(
                    resp, item.xpath('title/text()').extract()[0]))

    def article_parse(self, response, rss_title=None):
        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.ignored_allowed_domains[0], self.original_url,
            rss_title)

    @staticmethod
    def supports_site(url):
        """
        Sitemap-Crawler are supported by every site which have a
        Sitemap set in the robots.txt
        """

        # Follow redirects
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        redirect = opener.open(url).url
        response = urllib2.urlopen(redirect).read()

        # Check if "Sitemap" is set
        return re.search(r'(<link[^>]*href[^>]*type ?= ?"application\/rss\+xml"|<link[^>]*type ?= ?"application\/rss\+xml"[^>]*href)', response) is not None

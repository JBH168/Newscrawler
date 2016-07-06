# -*- coding: utf-8 -*-
import scrapy
import logging
import urllib2
from urlparse import urlparse
import re

from newscrawler.helper_classes.url_extractor import url_extractor


class sitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "sitemapCrawler"
    allowed_domains = None
    sitemap_urls = None
    original_url = None

    log = None

    config = None
    helper = None

    def __init__(self, helper, url, config, ignoreRegex, *args, **kwargs):
        self.log = logging.getLogger(__name__)

        self.config = config
        self.helper = helper
        self.original_url = url

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.sitemap_urls = [self.helper.url_extractor.get_sitemap_urls(url,
                             config.section('Crawler')
                             ['sitemapallowsubdomains'])]

        self.log.debug(self.sitemap_urls)

        super(sitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not re.match('text/html', response.headers.get('Content-Type')):
            self.log.warn("Dropped: %s's content is not of type "
                          "text/html but %s", response.url,
                          response.headers.get('Content-Type'))
            return

        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.allowed_domains[0], self.original_url)

    @staticmethod
    def supports_site(url):
        """
        Sitemap-Crawler are supported by every site which have a
        Sitemap set in the robots.txt
        """

        return url_extractor.sitemap_check(url)

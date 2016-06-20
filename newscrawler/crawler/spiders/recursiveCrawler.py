# -*- coding: utf-8 -*-
import scrapy

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector


class recursiveCrawler(scrapy.Spider):
    name = "recursiveCrawler"
    allowed_domains = None
    start_urls = None
    original_url = None

    config = None
    helper = None

    def __init__(self, helper, url, config, *args, **kwargs):
        self.config = config
        self.helper = helper

        self.original_url = url

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.start_urls = [self.helper.url_extractor.get_start_urls(url)]

        super(recursiveCrawler, self).__init__(*args, **kwargs)

        rules = [Rule(LinkExtractor(allow=('')),
                 callback='parse',
                 follow=True)]

    def parse(self, response):

        for request in self.helper.parse_crawler \
                .recursive_requests(response, self):
            yield request

        # if self.config.section('Crawler')['ignoresubdomains'] and \
        #         not self.helper.heuristics.is_from_subdomain(
        #         response.url, self.allowed_domains[0]):
        #     # TODO: Move to heuristics
        #     pass

        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.allowed_domains[0], self.original_url)

    @staticmethod
    def supports_site(url):
        """Recursive Crawler are supported by every site!"""
        return True

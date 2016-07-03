import re
import logging

import scrapy


class RecursiveCrawler(scrapy.Spider):
    name = "RecursiveCrawler"
    allowed_domains = None
    start_urls = None
    original_url = None

    log = None

    config = None
    helper = None

    ignore_regex = None
    ignore_file_extensions = None

    def __init__(self, helper, url, config, ignore_regex, *args, **kwargs):
        self.log = logging.getLogger(__name__)

        self.config = config
        self.helper = helper

        self.ignore_regex = ignore_regex
        self.ignore_file_extensions = self.config.section(
            'Crawler')['ignorefileextensions']

        self.original_url = url

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.start_urls = [self.helper.url_extractor.get_start_urls(url)]

        super(RecursiveCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        if not re.match('text/html', response.headers.get('Content-Type')):
            self.log.warn("Dropped: %s's content is not of type "
                          "text/html but %s", response.url,
                          response.headers.get('Content-Type'))
            return

        for request in self.helper.parse_crawler \
                .recursive_requests(response, self, self.ignore_regex,
                                    self.ignore_file_extensions):
            yield request

        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.allowed_domains[0], self.original_url)

    @staticmethod
    def supports_site(url):
        """Recursive Crawler are supported by every site!"""
        return True

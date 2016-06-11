# -*- coding: utf-8 -*-
import scrapy


class rssCrawler(scrapy.Spider):
    name = "rssCrawler"
    ignored_allowed_domains = None
    start_urls = None
    original_url = None

    config = None
    helper = None

    def __init__(self, helper, url, config, *args, **kwargs):
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
        for url in response.xpath('//item/link/text()').extract():
            yield scrapy.Request(url, callback=self.article_parse)

    def article_parse(self, response):

        # if self.config.section('Crawler')['ignoresubdomains'] and \
        #         not self.helper.heuristics.is_from_subdomain(
        #         response.url, self.allowed_domains[0]):
        #     # TODO: Move to heuristics
        #     pass

        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.ignored_allowed_domains[0], self.original_url)

# -*- coding: utf-8 -*-
import scrapy


class sitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "sitemapCrawler"
    allowed_domains = None
    sitemap_urls = None
    original_url = None

    config = None
    helper = None

    def __init__(self, helper, url, config, *args, **kwargs):
        self.config = config
        self.helper = helper
        self.original_url = url

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.sitemap_urls = [self.helper.url_extractor.get_sitemap_urls(url,
                             config.section('Crawler')
                             ['sitemapallowsubdomains'])]

        super(sitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):

        # if self.config.section('Crawler')['ignoresubdomains'] and \
        #         not self.helper.heuristics.is_from_subdomain(
        #         response.url, self.allowed_domains[0]):
        #     # TODO: Move to heuristics
        #     pass

        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.allowed_domains[0], self.original_url)

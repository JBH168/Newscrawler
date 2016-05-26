# -*- coding: utf-8 -*-
import scrapy


class SitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "SitemapCrawler"
    allowed_domains = None
    sitemap_urls = None

    helper = None
    resurive = False

    def __init__(self, helper, url, config, *args, **kwargs):
        self.logger.info(config.config())
        self.helper = helper

        self.allowed_domains = self.helper.url_extractor.get_allowed_domains(
                url)
        self.sitemap_urls = self.helper.url_extractor.get_sitemap_urls(
                url, config.section('Crawler')['sitemapallowsubdomains'])

        # TODO self.recursive = config.section('Crawler')['crawlingheuristics']

        super(SitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        # recursive crawling should be togglable
        if recursive:
            # Recursivly crawl all URLs on the current page
            for href in response.css("a::attr('href')"):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse)

        # heuristics
        if self.helper.heuristics.is_article(response):
            self.helper.download.save_webpage(response)

    # in case anything needs to be done after a crawler is done
    # def closed(self, reason):
    #     print reason

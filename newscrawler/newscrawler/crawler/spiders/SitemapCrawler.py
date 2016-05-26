# -*- coding: utf-8 -*-
import scrapy


class SitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "SitemapCrawler"
    allowed_domains = ["der-postillon.com"]
    sitemap_urls = ['http://www.der-postillon.com/robots.txt']

    helper = None

    def __init__(self, helper, config=None, json=None, *args, **kwargs):
        self.logger.info(config.config())
        self.helper = helper
        super(SitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        # recursive crawling should be togglable
        if False:
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

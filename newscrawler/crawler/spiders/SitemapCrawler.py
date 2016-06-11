# -*- coding: utf-8 -*-
import scrapy
from newscrawler.crawler.items import NewscrawlerItem

import time


class sitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "sitemapCrawler"
    allowed_domains = None
    sitemap_urls = None

    config = None
    helper = None

    original_url = None

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

        #if self.config.section('Crawler')['ignoresubdomains'] and \
        #        not self.helper.heuristics.is_from_subdomain(
        #        response.url, self.allowed_domains[0]):
            # TODO: Move to heuristics
        #    pass

        if self.helper.heuristics.is_article(response, self.original_url):
            timestamp = time.strftime('%y-%m-%d %H:%M:%S',
                                      time.gmtime(time.time()))
            article = NewscrawlerItem()
            article['localPath'] = self.helper.savepath_parser \
                .get_savepath(response.url)
            article['modifiedDate'] = timestamp
            article['downloadDate'] = timestamp
            article['sourceDomain'] = self.allowed_domains[0].encode("utf-8")
            article['url'] = response.url
            # TODO: response.selector.xpath("//h1/text()").extract()
            article['title'] = 'temp_title'
            article['ancestor'] = 'NULL'
            article['descendant'] = 'NULL'
            article['version'] = '1'
            article['spiderResponse'] = response
            yield article

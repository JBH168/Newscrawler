# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Item, Field
from scrapy.exceptions import DropItem

from newscrawler.crawler.items import NewscrawlerItem

import time


class SitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "SitemapCrawler"
    allowed_domains = None
    sitemap_urls = None

    config = None
    helper = None
    cwd = None

    def __init__(self, helper, url, config, *args, **kwargs):
        self.config = config
        self.helper = helper

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.sitemap_urls = [self.helper.url_extractor.get_sitemap_urls(url,
                             config.section('Crawler')
                             ['sitemapallowsubdomains'])]

        super(SitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):

        # TODO: this code-block breaks the pipeline (cause of yield),
        #       can be replaced with a Rule && LinkExtractor
        # http://doc.scrapy.org/en/latest/topics/link-extractors.html#topics-link-extractors
        # if self.config.section('Crawler')['recursivesitemap']:
        # Recursivly crawl all URLs on the current page
            # for href in response.css("a::attr('href')"):
                # url = response.urljoin(href.extract())
                # yield scrapy.Request(url, callback=self.parse)

        if self.helper.heuristics.is_article(response):
            timestamp = time.strftime('%y-%m-%d %H:%M:%S',
                                      time.gmtime(time.time()))
            article = NewscrawlerItem()
            article['localPath'] = self.helper.savepath_parser \
                .get_savepath(response.url)
            article['modifiedDate'] = timestamp
            article['downloadDate'] = timestamp
            article['sourceDomain'] = self.allowed_domains[0].encode("utf-8")
            article['url'] = response.url
            article['filename'] = '123123'  # TODO: remove this
            # TODO: response.selector.xpath("//h1/text()").extract()
            article['title'] = 'temp_title'
            article['ancestor'] = 'NULL'
            article['spiderResponse'] = response
            return article

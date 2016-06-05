# -*- coding: utf-8 -*-
import scrapy
import shutil
import os


class SitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "SitemapCrawler"
    allowed_domains = None
    sitemap_urls = None

    config = None
    helper = None
    cwd = None

    def __init__(self, helper, url, config, cwd, *args, **kwargs):
        self.config = config
        self.helper = helper

        self.cwd = cwd

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.sitemap_urls = [self.helper.url_extractor.get_sitemap_urls(url,
                             config.section('Crawler')
                             ['sitemapallowsubdomains'])]

        super(SitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        if self.config.section('Crawler')['recursivesitemap']:
            # Recursivly crawl all URLs on the current page
            for href in response.css("a::attr('href')"):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse)

        # heuristics
        if self.helper.heuristics.is_article(response):
            self.helper.download.save_webpage(response)

    def closed(self, reason):
        if self.config.section('Files')['removejobdironfinishedsignal'] \
                and reason == 'finished':
            shutil.rmtree(os.path.abspath(os.path.join(
                self.cwd, self.config.section('Scrapy')['jobdir'])))

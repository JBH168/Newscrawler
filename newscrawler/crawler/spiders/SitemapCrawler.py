# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Item, Field

class NewscrawlerItem(scrapy.Item):
    # ID of the article in the DB
    id = scrapy.Field()
    # Path of the file on the local filesystem
    localPath = scrapy.Field()
    # When the article was last modified
    modifiedDate = scrapy.Field()
    # When the article was downloaded
    downloadDate = scrapy.Field()
    # Root domain from which the article came
    sourceDomain = scrapy.Field()
    url = scrapy.Field()
    # Hashed filename for local storage
    filename = scrapy.Field()
    # Title of the article
    title = scrapy.Field()
    # Older version of the article in the DB, if exists
    ancestor = scrapy.Field()
    # Raw HTML data for local storage
    html = scrapy.Field()

class SitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "SitemapCrawler"
    allowed_domains = None
    sitemap_urls = None

    helper = None
    recursive = False

    def __init__(self, helper, url, config, *args, **kwargs):
        # self.logger.info(config.config())
        self.helper = helper

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.sitemap_urls = [self.helper.url_extractor.get_sitemap_urls(url,
                             config.section('Crawler')
                             ['sitemapallowsubdomains'])]

        self.recursive = config \
            .section('Crawler')['recursivesitemap']

        super(SitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):
        # recursive crawling should be togglable
        if self.recursive:
            # Recursivly crawl all URLs on the current page
            for href in response.css("a::attr('href')"):
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse)

        # heuristics
        if self.helper.heuristics.is_article(response):
            self.helper.download.save_webpage(response)

	#article = NewscrawlerItem()
        #article['localPath'] = '/testItem/'
        #article['modifiedDate'] = '1000-01-01 00:00:00'
        #article['downloadDate'] = '1000-01-01 00:00:00'
        #article['sourceDomain'] = 'zeit.de'
        #article['url'] = 'zeit.de/secret_files/'
        #article['filename'] = '123123'
        #article['title'] = 'Hello World'
        #article['ancestor'] = 'NULL'
	#return article

    # in case anything needs to be done after a crawler is done
    # def closed(self, reason):
    #     print reason

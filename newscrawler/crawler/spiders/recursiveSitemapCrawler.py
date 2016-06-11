# -*- coding: utf-8 -*-
import scrapy
from newscrawler.crawler.items import NewscrawlerItem

import time


class recursiveSitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "recursiveSitemapCrawler"
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

        super(recursiveSitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):

        # Recursivly crawl all URLs on the current page
        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())
            # http://www.yourhtmlsource.com/starthere/fileformats.html
            if re.match('.*\.(pdf)|(docx?)|(xlsx?)|(pptx?)|(epub)|'
                        '(jpe?g)|(png)|(bmp)|(gif)|(tiff)|(webp)|'
                        '(avi)|(mpe?g)|(mov)|(qt)|(webm)|(ogg)|'
                        '(midi)|(mid)|(mp3)|(wav)|'
                        '(zip)|(rar)|(exe)|(apk)|'
                        '(css)$', url, re.IGNORECASE) is None:
                yield scrapy.Request(url, callback=self.parse)

        if self.config.section('Crawler')['ignoresubdomains'] and \
                not self.helper.heuristics.is_from_subdomain(
                response.url, self.allowed_domains[0]):
            # TODO: Move to heuristics
            pass

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

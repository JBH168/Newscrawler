# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Item, Field
from scrapy.exceptions import DropItem
import shutil
import os


class NewscrawlerItem(scrapy.Item):
    ## ID of the article in the DB
    id = scrapy.Field()
    ## Path of the file on the local filesystem
    localPath = scrapy.Field()
    ## When the article was last modified
    modifiedDate = scrapy.Field()
    ## When the article was downloaded
    downloadDate = scrapy.Field()
    ## Root domain from which the article came
    sourceDomain = scrapy.Field()
    url = scrapy.Field()
    ## Hashed filename for local storage
    filename = scrapy.Field()
    ## Title of the article
    title = scrapy.Field()
    ## Older version of the article in the DB, if exists
    ancestor = scrapy.Field()
    ## Reponse object from crawler
    spiderResponse = scrapy.Field()

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
	
	### TODO: this code-block breaks the pipeline (cause of yield), can be replaced with a Rule && LinkExtractor
	### http://doc.scrapy.org/en/latest/topics/link-extractors.html#topics-link-extractors
        #if self.config.section('Crawler')['recursivesitemap']:   
	# Recursivly crawl all URLs on the current page
            #for href in response.css("a::attr('href')"):
             #   url = response.urljoin(href.extract())
              #  yield scrapy.Request(url, callback=self.parse)

	if self.helper.heuristics.is_article(response):
    		article = NewscrawlerItem()
        	article['localPath'] = self.helper.savepath_parser.get_savepath(response.url)
		article['modifiedDate'] = '1000-01-01 00:00:00' #####Filler
        	article['downloadDate'] = '1000-01-01 00:00:00' #####Filler
		article['sourceDomain'] = self.allowed_domains[0].encode("utf-8") 
		article['url'] = response.url 
        	article['filename'] = '123123' #######DO we need this?? 
        	article['title'] = 'temp_entry' ######Filler 
        	article['ancestor'] = 'NULL' 
		article['spiderResponse'] = response
		return article

    ### TODO: Causes errors on *nix
    ### 
    #def closed(self, reason):
    #    if self.config.section('Files')['removejobdironfinishedsignal'] \
    #            and reason == 'finished':
    #        shutil.rmtree(os.path.abspath(os.path.join(
    #            self.cwd, self.config.section('Scrapy')['jobdir'])))

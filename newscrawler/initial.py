#
# Initial Script
#
# called whenever a crawl should be executed
#
# reads in and parses json file via input.py
# calls the corresponding webcrawler with the input data
#
#
import os
from os import path
import sys

import logging

import scrapy
from scrapy.crawler import CrawlerProcess

from newscrawler.crawler.spiders.SitemapCrawler import SitemapCrawler

from newscrawler.config import CrawlerConfig
from newscrawler.config import JsonConfig

from newscrawler.crawler.helper import helper

class initial(object):
    cfg = None
    json = None
    log = None
    process = None
    helper = None
    def __init__(self):
        self.cfg = CrawlerConfig.get_instance()
        self.cfg.setup("./newscrawler.cfg")
        self.log = logging.getLogger(__name__)
        self.log.info("Config initalized - Further initialisation.")
        self.json = JsonConfig.get_instance()
        self.json.setup("./input_data.json")

        self.helper = helper()

        self.loadCrawler(SitemapCrawler)
        self.process.start()

    def loadCrawler(self, crawler):
        if self.process is None:
            self.process = CrawlerProcess()
        self.process.crawl(
            crawler,
            self.helper,
            config=self.cfg,
            json=self.json)



if __name__ == "__main__":
    initial()


# TODO: json parser to be called

# decide which webcrawler to call and pass arguments along
# http://doc.scrapy.org/en/latest/topics/spiders.html#spider-arguments
#
# process = CrawlerProcess()
# process.crawl(Crawler)
# # possible to run multiple crawlers simultaneously
# process.crawl(SitemapCrawler)
# process.start()

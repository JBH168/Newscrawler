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
        self.cfg.setup(self.get_abs_file_path("./newscrawler.cfg"))
        self.log = logging.getLogger(__name__)
        self.log.info("Config initalized - Further initialisation.")

        urlinput_file_path = self.cfg.section('Files')['urlinput']
        self.json = JsonConfig.get_instance()
        self.json.setup(self.get_abs_file_path(urlinput_file_path))

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

    def get_abs_file_path(self, rel_file_path):
        # for the following three lines of code, see:
        # http://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
        script_dir = os.path.dirname(__file__)  # absolute dir the script is in
        abs_file_path = os.path.abspath(
                            os.path.join(script_dir, rel_file_path))

        if not os.path.exists(abs_file_path):
            self.log.error(abs_file_path + " does not exist")

        return abs_file_path


if __name__ == "__main__":
    initial()


# decide which webcrawler to call and pass arguments along
# http://doc.scrapy.org/en/latest/topics/spiders.html#spider-arguments
#
# process = CrawlerProcess()
# process.crawl(Crawler)
# # possible to run multiple crawlers simultaneously
# process.crawl(SitemapCrawler)
# process.start()

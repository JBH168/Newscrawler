"""
This script should only be executed by the newscrawler initial script iteself.

This script starts a crawler.
"""

import os
import sys
import shutil

import hashlib
from ast import literal_eval

import logging

from scrapy.crawler import CrawlerProcess

from scrapy.settings import Settings
from scrapy.spiderloader import SpiderLoader

from scrapy.utils.log import configure_logging

from newscrawler.config import CrawlerConfig
from newscrawler.config import JsonConfig

from newscrawler.helper import Helper


class SingleCrawler(object):
    """
    This class is called when this script is executed

    for each url in the URL-input-json-file, it starts a crawler
    """
    cfg = None
    json = None
    log = None
    crawler = None
    process = None
    helper = None
    cfg_file_path = None
    json_file_path = None
    cfg_crawler = None
    __scrapy_options = None
    __crawer_module = "newscrawler.crawler.spiders"
    site_number = None
    shall_resume = False
    daemonize = 0

    def __init__(self, cfg_file_path, json_file_path,
                 site_index, shall_resume, daemonize):
        # set up logging before it's defined via the config file,
        # this will be overwritten and all other levels will be put out
        # as well, if it will be changed.
        configure_logging({"LOG_LEVEL": "CRITICAL"})
        self.log = logging.getLogger(__name__)

        self.cfg_file_path = cfg_file_path
        self.json_file_path = json_file_path
        self.site_number = int(site_index)
        self.shall_resume = shall_resume \
            if isinstance(shall_resume, bool) else literal_eval(shall_resume)
        self.daemonize = int(daemonize)

        # set up the config file
        self.cfg = CrawlerConfig.get_instance()
        self.cfg.setup(self.cfg_file_path)
        self.log.info("Config initalized - Further initialisation.")

        # load the URL-input-json-file
        self.json = JsonConfig.get_instance()
        self.json.setup(self.json_file_path)

        site = self.json.get_site_objects()[self.site_number]

        if "ignore_regex" in site:
            ignore_regex = '(' + site["ignoreRegex"] + ')|'
        else:
            ignore_regex = ''

        self.helper = Helper(self.cfg.section('Heuristics'),
                             self.cfg.section('Crawler')['savepath'],
                             self.cfg_file_path,
                             self.json.get_site_objects())

        self.__scrapy_options = self.cfg.get_scrapy_options()

        # lets start dat crawler
        if "crawler" in site:
            self.crawler = site["crawler"]
        else:
            self.crawler = self.cfg.section("Crawler")["default"]

        self.update_job_dir(site)

        # make sure the crawler does not resume crawling
        # if not stated otherwise in the arguments passed to this script
        self.remove_jobdir_if_not_resume()

        self.load_crawler(self.get_crawler(self.crawler), site["url"],
                          ignore_regex)

        self.process.start()

    def update_job_dir(self, site):
        """
        Update the JOBDIR in __scrapy_options for the crawler,
        so each crawler gets its own jobdir.
        """
        jobdir = self.__scrapy_options["JOBDIR"]
        if not jobdir.endswith("/"):
            jobdir = jobdir + "/"
        hashed = hashlib.md5(site["url"] + self.crawler)

        self.__scrapy_options["JOBDIR"] = jobdir + hashed.hexdigest()

    def get_crawler(self, crawler):
        settings = Settings()
        settings.set('SPIDER_MODULES', [self.__crawer_module])
        spider_loader = SpiderLoader(settings)
        return spider_loader.load(crawler)

    def load_crawler(self, crawler, url, ignore_regex):
        """
        loads the given crawler with the given url
        """
        self.process = CrawlerProcess(self.cfg.get_scrapy_options())
        self.process.crawl(
            crawler,
            self.helper,
            url=url,
            config=self.cfg,
            ignore_regex=ignore_regex)

    def remove_jobdir_if_not_resume(self):
        """
        if '--resume' isn't passed to this script, this method ensures that
        there's no JOBDIR (with the name and path stated in the config file)
        any crawler would automatically resume crawling with
        """
        jobdir = os.path.abspath(self.__scrapy_options["JOBDIR"])

        if (not self.shall_resume or self.daemonize > 0) \
                and os.path.exists(jobdir):
            shutil.rmtree(jobdir)

            self.log.info("Removed JOBDIR since '--resume' was not passed to"
                          " initial.py or this crawler was daemonized.")

if __name__ == "__main__":
    SingleCrawler(cfg_file_path=sys.argv[1],
                  json_file_path=sys.argv[2],
                  site_index=sys.argv[3],
                  shall_resume=sys.argv[4],
                  daemonize=sys.argv[5])
"""
This script should be called whenever a crawl should be executed

The first parameter, if passed to this script,
should be a path to a config file (*.cfg)
 - it can be absolute or relative
 - if it isn't passed along, scrapy will fall back to the default
   newscrawler.cfg
Another parameter that can be passed to this script is '--resume'
 - if this parameter isn't passed along, this script will delete the JOBDIR
   defined in the config file if it does exist
 - otherwise, any crawler will be called with this JOBDIR and resume crawling
"""

import os
import sys
import shutil

import logging
import importlib
import hashlib

from scrapy.crawler import CrawlerProcess

from newscrawler.crawler.spiders.sitemapCrawler import sitemapCrawler
from newscrawler.crawler.spiders.recursiveSitemapCrawler import recursiveSitemapCrawler
from newscrawler.crawler.spiders.recursiveCrawler import recursiveCrawler
from newscrawler.crawler.spiders.rssCrawler import rssCrawler

from newscrawler.config import CrawlerConfig
from newscrawler.config import JsonConfig

from newscrawler.helper import helper

from scrapy.utils.log import configure_logging
from ast import literal_eval


class initial(object):
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
    cfg_crawler = None
    __scrapy_options = None
    __crawer_module = "newscrawler.crawler.spiders"
    site_number = None
    shall_resume = False
    daemonize = 0

    def __init__(self):
        # set up logging before it's defined via the config file,
        # this will be overwritten and all other levels will be put out
        # as well, if it will be changed.
        configure_logging({"LOG_LEVEL": "CRITICAL"})
        self.log = logging.getLogger(__name__)

        self.site_number = int(sys.argv[2])
        self.shall_resume = literal_eval(sys.argv[3])
        self.daemonize = int(sys.argv[4])

        # set up the config file
        self.cfg = CrawlerConfig.get_instance()
        self.cfg_file_path = sys.argv[1]
        self.cfg.setup(self.cfg_file_path)
        self.log.info("Config initalized - Further initialisation.")

        # load the URL-input-json-file
        urlinput_file_path = self.cfg.section('Files')['urlinput']
        self.json = JsonConfig.get_instance()
        self.json.setup(self.get_abs_file_path(
            urlinput_file_path, quit_on_error=True))

        site = self.json.get_site_objects()[self.site_number]

        if "ignoreRegex" in site:
            ignoreRegex = '(' + site["ignoreRegex"] + ')|'
        else:
            ignoreRegex = ''

        self.helper = helper(self.cfg.section('Heuristics'),
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

        self.loadCrawler(self.getCrawler(self.crawler), site["url"],
                         ignoreRegex)

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

    def getCrawler(self, crawler):
        return getattr(importlib.import_module(self.__crawer_module + "." +
                                               crawler), crawler)

    def loadCrawler(self, crawler, url, ignoreRegex):
        """
        loads the given crawler with the given url
        """
        self.process = CrawlerProcess(self.cfg.get_scrapy_options())
        self.process.crawl(
            crawler,
            self.helper,
            url=url,
            config=self.cfg,
            ignoreRegex=ignoreRegex)

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
                          " initial.py")

    # TODO: move into a helper class; copy in initial.py
    def get_abs_file_path(self, rel_file_path, quit_on_error=None):
        """
        returns the absolute file path of the given relative file path
        to either this script or to the config file.

        May throw a RuntimeError if quit_on_error is True
        """
        if self.cfg_file_path is not None and \
                not self.cfg.section('General')['relativetoinitial']:
            script_dir = os.path.dirname(self.cfg_file_path)
        else:
            # absolute dir this script is in
            script_dir = os.path.dirname(__file__)

        abs_file_path = os.path.abspath(
            os.path.join(script_dir, rel_file_path))

        if not os.path.exists(abs_file_path):
            self.log.error(abs_file_path + " does not exist.")
            if quit_on_error is True:
                raise RuntimeError("Importet file not found. Quit.")

        return abs_file_path


if __name__ == "__main__":
    initial()

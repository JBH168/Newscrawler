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

from scrapy.crawler import CrawlerProcess

from newscrawler.crawler.spiders.SitemapCrawler import sitemapCrawler
from newscrawler.crawler.spiders.recursiveSitemapCrawler import recursiveSitemapCrawler
from newscrawler.crawler.spiders.recursiveCrawler import recursiveCrawler
from newscrawler.crawler.spiders.rssCrawler import rssCrawler

from newscrawler.config import CrawlerConfig
from newscrawler.config import JsonConfig

from newscrawler.helper import helper


class initial(object):
    """
    This class is called when this script is executed

    for each url in the URL-input-json-file, it starts a crawler
    """
    cfg = None
    json = None
    log = None
    process = None
    helper = None
    cfg_file_path = None
    __scrapy_options = None

    def __init__(self):
        # set up logging before it's defined via the config file
        logging.basicConfig(format="[%(name)s:%(lineno)d|"
                            "%(levelname)s] %(message)s",
                            level="DEBUG")
        self.log = logging.getLogger(__name__)

        # set up the config file
        self.cfg = CrawlerConfig.get_instance()
        self.cfg_file_path = self.get_config_file_path()
        self.cfg.setup(self.cfg_file_path)
        self.log.info("Config initalized - Further initialisation.")

        # load the URL-input-json-file
        urlinput_file_path = self.cfg.section('Files')['urlinput']
        self.json = JsonConfig.get_instance()
        self.json.setup(self.get_abs_file_path(
            urlinput_file_path, quit_on_error=True))

        self.helper = helper(self.cfg.section('Heuristics'),
                             self.cfg.section('Crawler')['savepath'],
                             self.cfg_file_path,
                             self.json.get_site_objects())

        # make sure the crawler does not resume crawling
        # if not stated otherwise in the arguments passed to this script
        self.remove_jobdir_if_not_resume()

        """
        starts a cralwer for each url in the read-in file
        """
        if self.cfg.section('Crawler')['sitemap']:
            for url in self.json.get_url_array():
                self.loadCrawler(sitemapCrawler, url)
        else:
            for url in self.json.get_url_array():
                self.loadCrawler(recursiveCrawler, url)

        self.process.start()

    def loadCrawler(self, crawler, url):
        """
        loads the given crawler with the given url
        """
        if self.process is None:
            self.process = CrawlerProcess(self.get_scrapy_options())
        self.process.crawl(
            crawler,
            self.helper,
            url=url,
            config=self.cfg)

    def get_config_file_path(self):
        """
        returns the config file path
         - if passed to this script, ensures it's a valid file path
         - if not passed to this script or not valid, falls back to the
           standard ./newscrawler.cfg
        """
        # test if the config file path was passed to this script
        # argv[0] should be this script's name
        # argv[1] should be the config file path
        #   for path names with spaces, use "path"
        if len(sys.argv) > 1:
            input_config_file_path = os.path.abspath(sys.argv[1])

            if os.path.exists(input_config_file_path) and os.path.splitext(
                    input_config_file_path)[1] == ".cfg":
                return input_config_file_path
            else:
                self.log.error("First argument passed to initial.py is not"
                               " the config file. Falling back to"
                               " ./newscrawler.cfg.")

        # Default
        return self.get_abs_file_path("./newscrawler.cfg", quit_on_error=True)

    def remove_jobdir_if_not_resume(self):
        """
        if '--resume' isn't passed to this script, this method ensures that
        there's no JOBDIR (with the name and path stated in the config file) in
        the cwd any crawler would resume crawling with
        """
        jobdir = os.path.abspath(self.cfg.section('Scrapy')['jobdir'])

        if len([arg for arg in sys.argv if arg == '--resume']) == 0 \
                and os.path.exists(jobdir):
            shutil.rmtree(jobdir)

            self.log.info("Removed JOBDIR since '--resume' was not passed to"
                          " initial.py")

    def get_scrapy_options(self):
        """
        returns all the options listed in the config section 'Scrapy'
        """
        if self.__scrapy_options is None:
            self.__scrapy_options = {}
            options = self.cfg.section("Scrapy")

            for key, value in options.items():
                self.__scrapy_options[key.upper()] = value

        return self.__scrapy_options

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

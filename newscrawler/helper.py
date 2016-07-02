"""
This file's only purpose is to bundle all helper classes in ./helper_classes
so they can be passed to other classes easily
"""

from helper_classes.heuristics import Heuristics
from helper_classes.url_extractor import UrlExtractor
from helper_classes.savepath_parser import SavepathParser
from helper_classes.parse_crawler import ParseCrawler


class Helper(object):
    """
    This class contains helper classes from ./helper_classes
    This class and its helper-classes is passed to all crawlers
    """
    heuristics = None
    url_extractor = None
    savepath_parser = None
    parse_crawler = None

    def __init__(
            self,
            cfg_heuristics,
            cfg_savepath,
            cfg_file_path,
            sites_object
    ):
        self.heuristics = Heuristics(cfg_heuristics, sites_object)
        self.url_extractor = UrlExtractor()
        self.savepath_parser = SavepathParser(cfg_savepath,
                                              cfg_file_path, self)
        self.parse_crawler = ParseCrawler(self)

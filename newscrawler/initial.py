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

import scrapy
from scrapy.crawler import CrawlerProcess

from newscrawler.config import config

# crawlers
from newscrawler.spiders.crawler import Crawler
from newscrawler.spiders.SitemapCrawler import SitemapCrawler

# test if the json file path was passed to the script
# argv[0] should be this script's name
# argv[1] should be the json file path
#   for path names with spaces, use "path"
if len(sys.argv) > 1:
    input_json_file_path = os.path.abspath(sys.argv[1])

    if not os.path.exists(input_json_file_path):
        print input_json_file_path + " does not exist"
        quit()

    if not os.path.splitext(input_json_file_path)[1] == ".json":
        print input_json_file_path + " if not a valid json file path"
        quit()

else:
    print "json file path missing"
    quit()


# TODO: json parser to be called

# decide which webcrawler to call and pass arguments along
# http://doc.scrapy.org/en/latest/topics/spiders.html#spider-arguments
#
# process = CrawlerProcess()
# process.crawl(Crawler)
# # possible to run multiple crawlers simultaneously
# process.crawl(SitemapCrawler)
# process.start()

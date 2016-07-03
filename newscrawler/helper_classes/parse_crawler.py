"""
This is a helper class for the crawler's parse methods
"""
import time
import re

import scrapy
from newscrawler.crawler.items import NewscrawlerItem


class ParseCrawler(object):
    """
    helper class
    """
    helper = None

    def __init__(self, helper):
        self.helper = helper

    def pass_to_pipeline_if_article(
            self,
            response,
            source_domain,
            original_url,
            rss_title=None
    ):
        if self.helper.heuristics.is_article(response, original_url):
            timestamp = time.strftime('%y-%m-%d %H:%M:%S',
                                      time.gmtime(time.time()))

            article = NewscrawlerItem()
            article['local_path'] = self.helper.savepath_parser \
                .get_savepath(response.url)
            article['absLocalPath'] = self.helper.savepath_parser.get_abs_path(
                article['local_path'])
            article['modified_date'] = timestamp
            article['download_date'] = timestamp
            article['source_domain'] = source_domain.encode("utf-8")
            article['url'] = response.url
            article['html_title'] = response.selector.xpath('//title/text()') \
                .extract_first().encode("utf-8")
            if rss_title is None:
                article['rss_title'] = 'NULL'
            else:
                article['rss_title'] = rss_title
            article['ancestor'] = 'NULL'
            article['descendant'] = 'NULL'
            article['version'] = '1'
            article['spiderResponse'] = response
            return article

    @staticmethod
    def recursive_requests(response, spider, ignore_regex='',
                           ignore_file_extensions='pdf'):
        # Recursivly crawl all URLs on the current page
        # that do not point to irrelevant file types
        # or contain any of the given ignore_regex regexes
        return [scrapy.Request(response.urljoin(href), callback=spider.parse)
                for href in response.css("a::attr('href')").extract()
                if re.match(r'.*\.' + ignore_file_extensions + r'$',
                            response.urljoin(href), re.IGNORECASE) is None and
                len(re.match(ignore_regex,
                             response.urljoin(href)).group(0)) == 0]

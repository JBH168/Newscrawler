"""
This is a helper class for the crawler's parse methods
"""
import scrapy
from newscrawler.crawler.items import NewscrawlerItem

import time
import re


class parse_crawler(object):
    """
    helper class
    """
    helper = None

    def __init__(self, helper):
        self.helper = helper

    def pass_to_pipeline_if_article(
            self,
            response,
            sourceDomain,
            original_url,
            rss_title=None
    ):
        if self.helper.heuristics.is_article(response, original_url):
            timestamp = time.strftime('%y-%m-%d %H:%M:%S',
                                      time.gmtime(time.time()))

            article = NewscrawlerItem()
            article['localPath'] = self.helper.savepath_parser \
                .get_savepath(response.url)
            article['modifiedDate'] = timestamp
            article['downloadDate'] = timestamp
            article['sourceDomain'] = sourceDomain[0].encode("utf-8")
            article['url'] = response.url
            article['title'] = response.selector.xpath('//title/text()') \
                .extract_first().encode("utf-8")
            # if rss_title is None:
            #     article['rss_title'] = 'NULL'
            # else:
            #     article['rss_title'] = rss_title
            article['ancestor'] = 'NULL'
            article['descendant'] = 'NULL'
            article['version'] = '1'
            article['spiderResponse'] = response
            return article

    def recursive_requests(self, response, spider):
        # Recursivly crawl all URLs on the current page
        # that do not point to irrelevant file types
        return [scrapy.Request(response.urljoin(href), callback=spider.parse)
                for href in response.css("a::attr('href')").extract()
                if re.match('.*\.(pdf)|(docx?)|(xlsx?)|(pptx?)|(epub)|'
                            '(jpe?g)|(png)|(bmp)|(gif)|(tiff)|(webp)|'
                            '(avi)|(mpe?g)|(mov)|(qt)|(webm)|(ogg)|'
                            '(midi)|(mid)|(mp3)|(wav)|'
                            '(zip)|(rar)|(exe)|(apk)|'
                            '(css)$', response.urljoin(href), re.IGNORECASE
                            ) is None]
# -*- coding: utf-8 -*-
import scrapy


class Crawler(scrapy.Spider):
    name = "Crawler"
    allowed_domains = ["der-postillon.com"]
    start_urls = (
        'http://www.der-postillon.com/',
    )

    helper = None

    def __init__(self, helper, url, config, *args, **kwargs):
        self.logger.info(config.config())
        self.helper = helper

        self.allowed_domains = self.helper.url_extractor.get_allowed_domains(
                url)
        self.start_urls = self.helper.url_extractor.get_start_urls(url)

        super(Crawler, self).__init__(*args, **kwargs)

    # http://doc.scrapy.org/en/latest/topics/spiders.html
    #
    # This method must return an iterable with the first Requests to crawl for
    # this spider. This is the method called by Scrapy when the spider is
    # opened for scraping when no particular URLs are specified.
    #
    # For example, if you need to start by logging in using a POST request,
    # you could do:
    #
    # def start_requests(self):
    #     return [scrapy.FormRequest("http://www.example.com/login",
    #                            formdata={'user': 'john', 'pass': 'secret'},
    #                            callback=self.logged_in)]
    # def logged_in(self, response):
    #     # here you would extract links to follow and return Requests for
    #     # each of them, with another callback
    #     pass

    def parse(self, response):
        # Recursivly crawl all URLs on the current page
        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse)

        # heuristics
        if self.helper.heuristics.is_article(response):
            self.helper.download.save_webpage(response)

    # in case anything needs to be done after a crawler is done
    # def closed(self, reason):
    #     print reason

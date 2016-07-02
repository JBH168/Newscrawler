import urllib2
from urlparse import urlparse

import scrapy


class RecursiveSitemapCrawler(scrapy.spiders.SitemapSpider):
    name = "RecursiveSitemapCrawler"
    allowed_domains = None
    sitemap_urls = None
    original_url = None

    config = None
    helper = None

    ignore_regex = None
    ignore_file_extensions = None

    def __init__(self, helper, url, config, ignore_regex, *args, **kwargs):
        self.config = config
        self.helper = helper

        self.ignore_regex = ignore_regex
        self.ignore_file_extensions = self.config.section(
            'Crawler')['ignorefileextensions']

        self.original_url = url

        self.allowed_domains = [self.helper.url_extractor
                                .get_allowed_domains(url)]
        self.sitemap_urls = [self.helper.url_extractor.get_sitemap_urls(
            url, config.section('Crawler')['sitemapallowsubdomains'])]

        super(RecursiveSitemapCrawler, self).__init__(*args, **kwargs)

    def parse(self, response):

        for request in self.helper.parse_crawler \
                .recursive_requests(response, self, self.ignore_regex,
                                    self.ignore_file_extensions):
            yield request

        yield self.helper.parse_crawler.pass_to_pipeline_if_article(
            response, self.allowed_domains[0], self.original_url)

    # TODO: move; copy in sitemapCrawler.py
    @staticmethod
    def supports_site(url):
        """
        Sitemap-Crawler are supported by every site which have a
        Sitemap set in the robots.txt
        """

        # Follow redirects
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        redirect = opener.open(url).url

        # Get robots.txt
        parsed = urlparse(redirect)
        robots = '{url.scheme}://{url.netloc}/robots.txt'.format(url=parsed)
        response = urllib2.urlopen(robots)

        # Check if "Sitemap" is set
        return "Sitemap:" in response.read()

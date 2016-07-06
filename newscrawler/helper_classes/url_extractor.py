"""
helper class for url extraction
"""
import re
import os

import urllib2
from urlparse import urlparse


class UrlExtractor(object):

    """
    This class contains methods to extract parts of any given url
    """

    @staticmethod
    def get_allowed_domains(url):
        """
        returns subdomains.domain.topleveldomain of url
        """
        return re.sub(r'^(www.)', '', re.search(r'[^/]+\.[^/]+', url).group(0))

    @staticmethod
    def get_allowed_domains_without_subdomains(url):
        """
        returns domain.topleveldomain of url
        """
        return re.search(r'[^/.]+\.[^/.]+$',
                         UrlExtractor.get_allowed_domains(url)).group(0)

    @staticmethod
    def get_subdomains(url):
        """
        returns subdomains of url
        """
        allowed_domains = UrlExtractor.get_allowed_domains(url)
        return allowed_domains[:len(allowed_domains) - len(
            UrlExtractor.get_allowed_domains_without_subdomains(url))]

    @staticmethod
    def follow_redirects(url):
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        return opener.open(url).url

    @staticmethod
    def get_sitemap_urls(url, allow_subdomains):
        """
        returns http://subdomains.domain.topleveldomain/robots.txt of url

        allow_subdomains decides if the return contains the subdomains
        """
        if allow_subdomains:
            redirect = UrlExtractor.follow_redirects(
                "http://" + UrlExtractor.get_allowed_domains(url)
                )
        else:
            redirect = UrlExtractor.follow_redirects(
                "http://" +
                UrlExtractor.get_allowed_domains_without_subdomains(url)
                )
        redirect = UrlExtractor.follow_redirects(url)

        # Get robots.txt
        parsed = urlparse(redirect)
        robots = '{url.scheme}://{url.netloc}/robots.txt'.format(url=parsed)

        try:
            urllib2.urlopen(robots)
            return robots
        except:
            if allow_subdomains:
                return UrlExtractor.get_sitemap_urls(url, False)
            else:
                raise Exception('Fatal: no robots.txt found.')

    @staticmethod
    def sitemap_check(url):
        """
        Sitemap-Crawler are supported by every site which have a
        Sitemap set in the robots.txt
        """
        response = urllib2.urlopen(UrlExtractor.get_sitemap_urls(url, True))

        # Check if "Sitemap" is set
        return "Sitemap:" in response.read()

    def get_rss_url(self, response):
        """
        return the rss url
        a link of type "application/rss+rml" of the webpage to the given url
        """
        # if this throws an IndexError, then the webpage with the given url
        # does not contain a link of type "application/rss+xml"
        return response.xpath(
            '//link[contains(@type, "application/rss+xml")]').xpath(
                '@href').extract()[0]

    @staticmethod
    def get_start_urls(url):
        """
        returns http://subdomains.domain.topleveldomain/ of url
        """
        allowed_domains = UrlExtractor.get_allowed_domains(url)
        return "http://" + allowed_domains + "/"

    @staticmethod
    def get_url_directory_string(url):
        """
        returns the directory string on the server
        """
        domain = UrlExtractor.get_allowed_domains(url)

        splitted_url = url.split('/')

        # the following commented list comprehension could replace
        # the following for, if not and break statement
        # index = [index for index in range(len(splitted_url))
        #          if not re.search(domain, splitted_url[index]) is None][0]
        for index in range(len(splitted_url)):
            if not re.search(domain, splitted_url[index]) is None:
                if splitted_url[-1] is "":
                    splitted_url = splitted_url[index + 1:-2]
                else:
                    splitted_url = splitted_url[index + 1:-1]
                break

        return '_'.join(splitted_url)

    @staticmethod
    def get_url_file_name(url):
        """
        returns the filename (without the file extension) on the server
        """
        url_root_ext = os.path.splitext(url)

        # len(".markdown") = 9
        if len(url_root_ext[1]) < 10:
            return os.path.split(url_root_ext[0])[1]
        else:
            return os.path.split(url)[1]

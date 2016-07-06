"""
Helper class for url extraction.
"""
import re
import os

import urllib2
from urlparse import urlparse


# len(".markdown") = 9
MAX_FILE_EXTENSION_LENGTH = 9


class UrlExtractor(object):
    """
    This class contains url related methods.
    """

    @staticmethod
    def get_allowed_domains(url):
        """
        Determines the url's domain.

        :param str url: the url to extract the allowed domain from
        :return str: subdomains.domain.topleveldomain of url
        """
        return re.sub(r'^(www.)', '', re.search(r'[^/]+\.[^/]+', url).group(0))

    @staticmethod
    def get_allowed_domains_without_subdomains(url):
        """
        Determines the url's domain ignoreing any subdomains.

        :param str url: the url to extract the allowed domain from
        :return str: domain.topleveldomain of url
        """
        return re.search(r'[^/.]+\.[^/.]+$',
                         UrlExtractor.get_allowed_domains(url)).group(0)

    @staticmethod
    def get_subdomains(url):
        """
        Determines the domain's subdomains.

        :param str url: the url to extract any subdomains from
        :return str: subdomains of url
        """
        allowed_domains = UrlExtractor.get_allowed_domains(url)
        return allowed_domains[:len(allowed_domains) - len(
            UrlExtractor.get_allowed_domains_without_subdomains(url))]

    @staticmethod
    def follow_redirects(url):
        """
        Get's the url actual address by following forwards

        :param str url: the url to work on
        :return str: actual address of url
        """
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        return opener.open(url).url

    @staticmethod
    def get_sitemap_urls(url, allow_subdomains):
        """
        Determines the domain's robot.txt

        :param str url: the url to work on
        :param bool allow_subdomains: Determines if the robot.txt may be the
                                      subdomain's
        :return: the robot.txt's address
        :raises Exception: if there's no robot.txt on the site's domain
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
        Sitemap set in the robots.txt.

        :param str url: the url to work on
        :return bool: Determines if Sitemap is set in the site's robots.txt
        """
        response = urllib2.urlopen(UrlExtractor.get_sitemap_urls(url, True))

        # Check if "Sitemap" is set
        return "Sitemap:" in response.read()

    def get_rss_url(self, response):
        """
        Extracts the rss feed's url from the scrapy response.

        :param scrapy_response response: the site to extract the rss feed from
        :return str: rss feed url
        """
        # if this throws an IndexError, then the webpage with the given url
        # does not contain a link of type "application/rss+xml"
        return response.xpath(
            '//link[contains(@type, "application/rss+xml")]').xpath(
                '@href').extract()[0]

    @staticmethod
    def get_start_urls(url):
        """
        Determines the start url to start a crawler from

        :param str url: the url to extract the start url from
        :return str: http://subdomains.domain.topleveldomain/ of url
        """
        return "http://" + UrlExtractor.get_allowed_domains(url) + "/"

    @staticmethod
    def get_url_directory_string(url):
        """
        Determines the url's directory string.

        :param str url: the url to extract the directory string from
        :return str: the directory string on the server
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
        Determines the url's file name.

        :param str url: the url to extract the file name from
        :return str: the filename (without the file extension) on the server
        """
        url_root_ext = os.path.splitext(url)

        if len(url_root_ext[1]) <= MAX_FILE_EXTENSION_LENGTH:
            return os.path.split(url_root_ext[0])[1]
        else:
            return os.path.split(url)[1]

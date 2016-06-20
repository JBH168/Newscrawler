"""
helper class for url extraction
"""

import re
import os


class url_extractor(object):

    """
    This class contains methods to extract parts of any given url
    """
    def get_allowed_domains(self, url):
        """
        returns subdomains.domain.topleveldomain of url
        """
        return re.sub(r'^(www.)', '', re.search(r'[^/]+\.[^/]+', url).group(0))

    def get_allowed_domains_without_subdomains(self, url):
        """
        returns domain.topleveldomain of url
        """
        return re.search(r'[^/.]+\.[^/.]+$',
                         self.get_allowed_domains(url)).group(0)

    def get_sitemap_urls(self, url, allow_subdomains):
        """
        returns http://subdomains.domain.topleveldomain/robots.txt of url

        allow_subdomains decides if the return contains the subdomains
        """
        if allow_subdomains:
            return "http://" + self.get_allowed_domains(url) + "/robots.txt"
        else:
            return "http://" + \
                    self.get_allowed_domains_without_subdomains(url) + \
                    "/robots.txt"

    def get_rss_url(self, response):
        """
        return the rss url
        a link of type "application/rss+rml" of the webpage to the given url
        """
        # if this throws an IndexError, then the webpage with the given url
        # does not contain a link of type "application/rss+xml"
        return response.xpath('//link[contains(@type, "application/rss+xml")]'
                              ).xpath('@href').extract()[0]

    def get_start_urls(self, url):
        """
        returns http://subdomains.domain.topleveldomain/ of url
        """
        allowed_domains = self.get_allowed_domains(url)
        return "http://" + allowed_domains + "/"

    def get_url_directory_string(self, url):
        """
        returns the directory string on the server
        """
        domain = self.get_allowed_domains(url)

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

    def get_url_file_name(self, url):
        """
        returns the filename (without the file extension) on the server
        """
        url_root_ext = os.path.splitext(url)

        # len(".markdown") = 9
        if (len(url_root_ext[1]) < 10):
            return os.path.split(url_root_ext[0])[1]
        else:
            return os.path.split(url)[1]

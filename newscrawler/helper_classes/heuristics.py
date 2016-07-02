"""
helper class for testing heuristics
"""
import re
from sub_classes.heuristics_manager import HeuristicsManager
from url_extractor import url_extractor


class Heuristics(HeuristicsManager):
    """
    helper class
    """

    @staticmethod
    def og_type(response, site_object):
        """
        Check if the site contains a meta-tag which contains
        property="og:type" and content="article"

        :return bool: true if the tag is contained.
        """
        og_type_article = response.xpath('//meta') \
            .re('(property="og:type".*content="article")|'
                '(content="article".*property="og:type")')
        if not og_type_article:
            return False

        return True

    def linked_headlines(self, response, site_object, check_self=False):
        """
        Checks how many of the headlines on the site contain links.
        :param response: The scrapy response
        :param site_object: The site object from the JSON-File
        :param check_self: Check headlines/
                                      headlines_containing_link_to_same_domain
                           instead of headline/headline_containing_link

        :return float: ratio headlines/headlines_containing_link
        """
        h_all = 0
        h_linked = 0
        domain = url_extractor.get_allowed_domains_without_subdomains(
            site_object["url"])

        # This regex checks, if a link containing site_domain as domain
        # is contained in a string.
        site_regex = r"href=[\"'][^\/]*\/\/(?:[^\"']*\.|)%s[\"'\/]" % domain
        for i in range(1, 7):
            for h in response.xpath('//h%s' % i).extract():
                # h_all += 1
                h_all += 1
                if "href" in h and (not check_self or
                                    re.search(site_regex, h) is not None):
                    h_linked += 1

        self.log.info("Linked headlines test: headlines = %s, linked = %s",
                      h_all, h_linked)

        min_headlines = self.cfg_heuristics["min_headlines_for_linked_test"]
        if min_headlines > h_all:
            self.log.info("Linked headlines test: Not enough headlines "
                          "(%s < %s): Passing!", h_all, min_headlines)
            return True

        return float(h_linked) / float(h_all)

    def self_linked_headlines(self, response, site_object):
        """
        Checks how many of the headlines on the site contain links.
        :param response: The scrapy response
        :param site_object: The site object from the JSON-File

        :return float: ratio headlines/headlines_containing_link_to_same_domain
        """
        return self.linked_headlines(response, site_object, True)

    def is_not_from_subdomain(self, response, site_object):
        """
        ensures the given url isn't from a subdomain
        """
        return url_extractor.get_allowed_domains(response.url) \
            == site_object["url"]

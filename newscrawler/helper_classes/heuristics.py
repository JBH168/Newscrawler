"""
helper class for testing heuristics
"""
from sub_classes.heuristics_manager import heuristics_manager


class heuristics(heuristics_manager):
    """
    helper class
    """
    url_extractor = None

    def __init__(self, url_extractor):
        self.url_extractor = url_extractor

    #
    # HEURISTICS

    def og_type(self, response):
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

    def linked_headlines(self, response):
        """
        Checks how many of the headlines on the site contain links.

        :return float: ration headlines/headlines_containing_link
        """
        # hcount = {}
        hAll_all = 0
        hAll_linked = 0
        for i in range(1, 7):
            # h_all = 0
            # h_linked = 0
            for h in response.xpath('//h%s' % i).extract():
                # h_all += 1
                hAll_all += 1
                if "href" in h:
                    # h_linked += 1
                    hAll_linked +=1

            # hcount['h%s' % i] = (h_all, h_linked)
        self.log.info("Linked headlines test: headlines = %s, linked = %s" %
                      (hAll_all, hAll_linked))

        min_headlines = self.cfg_heuristics["min_headlines_for_linked_test"]
        if min_headlines > hAll_all:
            self.log.info("Linked headlines test: Not enough headlines "
                          "(%s < %s): Passing!" % (hAll_all, min_headlines))
            return True

        return float(hAll_linked) / float(hAll_all)

    def is_from_subdomain(self, url, allowed_domains):
        """
        ensures the given url isn't from a subdomain
        """
        return self.url_extractor.get_allowed_domains(url) == allowed_domains

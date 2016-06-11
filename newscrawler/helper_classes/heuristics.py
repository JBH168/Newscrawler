"""
helper class for testing heuristics
"""


class heuristics(object):
    """
    helper class
    """
    cfg_heuristics = None
    url_extractor = None

    def __init__(self, cfg_heuristics, url_extractor):
        self.cfg_heuristics = cfg_heuristics
        self.url_extractor = url_extractor

    def is_article(self, response):
        """
        tests if the given response is an article

        returns False if any (in the config file) enabled heuritic fails
        returns True if all (in the config file) enabled heuristics succeed
        """
        # heuristic 1
        #     og:typ instead of og:type and articl instead of article
        #     since, for whatever reason, some webpages seem to forget about
        #     the last letter of some words...
        if self.cfg_heuristics["og_type_article"] \
            and not response.xpath('//meta[contains(@property, "og:typ")]'
                                   '[contains(@content, "articl")]'):
            return False
            # og_type_article = response.xpath('//meta') \
            #     .re('(property="og:type" content="article")|'
            #         '(content="article" property="og:type")')
            # if not og_type_article:
            #     return False

        # # heuristic 2
        # if self.cfg_heuristics[""]:

        # no more heuristics -> probably an article
        return True

    def is_from_subdomain(self, url, allowed_domains):
        """
        ensures the given url isn't from a subdomain
        """
        return self.url_extractor.get_allowed_domains(url) == allowed_domains

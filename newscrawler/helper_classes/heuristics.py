"""
helper class for testing heuristics
"""


class heuristics(object):
    """
    helper class

    contains a method that tests if a given response is an article
    """
    cfg_heuristics = None

    def __init__(self, cfg_heuristics):
        self.cfg_heuristics = cfg_heuristics

    def is_article(self, response):
        """
        tests if the given response is an article

        returns False if any (in the config file) enabled heuritic fails
        returns True if all (in the config file) enabled heuristics succeed
        """
        # heuristic 1
        if self.cfg_heuristics["og_type_article"]:
            og_type_article = response.xpath('//meta') \
                .re('(property="og:type" content="article")|'
                    '(content="article" property="og:type")')
            if not og_type_article:
                return False

        # # heuristic 2
        # if self.cfg_heuristics[""]:

        # no more heuristics -> probably an article
        return True

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
        return self.og_type(response)

    def og_type(self, response):
        """
        tests if the given response is an article

        returns False if any (in the config file) enabled heuritic fails
        returns True if all (in the config file) enabled heuristics succeed
        """
        # heuristic 1
        if self.cfg_heuristics["og_type_article"]:
            og_type_article = response.xpath('//meta') \
                .re('(property="og:type".*content="article")|'
                    '(content="article".*property="og:type")')
            if not og_type_article:
                return False

        # # heuristic 2
        # if self.cfg_heuristics[""]:

        # no more heuristics -> probably an article
        return True

    def linked_headlines(self, response):
        hcount = {}
        for i in range(1, 7):
            h_all = 0
            h_linked = 0
            for h in response.xpath('//h%s' % i).extract():
                h_all += 1
                if "href" in h:
                    h_linked += 1

            hcount['h%s' % i] = (h_all, h_linked)
        return hcount

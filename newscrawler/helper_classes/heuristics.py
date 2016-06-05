
class heuristics(object):
    cfg_heuristics = None

    def __init__(self, cfg_heuristics):
        self.cfg_heuristics = cfg_heuristics

    def is_article(self, response):
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

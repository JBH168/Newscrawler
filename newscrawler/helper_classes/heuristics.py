
class heuristics(object):
    def is_article(self, response):
        # heuristic 1
        og_type_article = response.xpath('//meta').re('(property="og:type" content="article")|(content="article" property="og:type")')
        if not og_type_article:
            return False

        # no more heuristics -> probably an article
        return True

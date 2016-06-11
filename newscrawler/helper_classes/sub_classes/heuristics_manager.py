import logging


class heuristics_manager(object):
    """
    This class is for managing the heuristics of a heuristics file (../heuristics.py) and adding the methods needed to check the heuristic (is_article).

    The heuristics file must inherit this class.

    The config is provided in self.cfg_heuristics,
    and logging is provided in self.log.
    """
    cfg_heuristics = None
    log = None

    __sites_object = {}
    __sites_heuristics = {}


    def __init__(self, cfg_heuristics, sites_object):
        self.cfg_heuristics = cfg_heuristics
        for site in sites_object:
            self.__sites_object[site["url"]] = site
        self.log = logging.getLogger(__name__)

    def is_article(self, response, url):
        """
        Tests if the given response is an article by calling and checking
        the heuristics set in newscrawler.cfg and input_data.json

        :param response: The response of the site.
        :param url: The base_url
                    (needed to get the site-specific config from the JSON-file)
        :return bool, true if the heuristics match the site as an article
        """
        site = self.__sites_object[url]
        heuristics = self.__get_enabled_heuristics(url)

        is_article = True

        for heuristic, condition in heuristics.iteritems():
            heuristic_func = getattr(self, heuristic)
            result = heuristic_func(response)
            check = self.__evaluate_result(result, condition)
            is_article = check and is_article
            self.log.info("Checking heuristic (%s)"
                          " result (%s) on condition (%s): %s" %
                          (heuristic, result, condition, check))

        self.log.info("Article accepted: %s" % is_article)
        return is_article

    def __evaluate_result(self, result, condition):
        """
        Evaluates a result of a heuristic with the condition given in the config

        Arguments:
        :param result: The result of the heuristic
        :param condition: The condition string to evaluate on the result
        :return bool, whether the heuristic result matches the condition
        """

        # If result is bool this means, that the heuristic
        # is bool as well or has a special situation
        # (for example some condition [e.g. in config] is [not] met, thus
        #  just pass it)
        if isinstance(result, bool):
            return result

        # Check if the condition is a String condition,
        # allowing <=, >=, <, >, = conditions or string
        # when they start with " or '
        if isinstance(condition, basestring):

            # Check if result should match a string
            if (condition.startswith("'") and condition.endswith("'")) or\
               (condition.startswith('"') and condition.endswith('"')):
                if isinstance(result, basestring):
                    self.log.debug("Condition %s recognized as string." % condition)
                    return result == condition[1:-1]
                return self.__evaluation_error(result, condition, "Result not string")

            # Only number-comparision following
            if not isinstance(result, (float, int)):
                return self.__evaluation_error(result, condition, "Result not number on comparision")

            # Check if result should match a number
            if condition.startswith("="):
                number = self.__try_parse_number(condition[1:])
                if isinstance(number, bool):
                    return self.__evaluation_error(result, condition, "Number not parsable (=)")
                return result == number

            # Check if result should be >= then a number
            if condition.startswith(">="):
                number = self.__try_parse_number(condition[2:])
                if isinstance(number, bool):
                    return self.__evaluation_error(result, condition, "Number not parsable (>=)")
                return result >= number

            # Check if result should be <= then a number
            if condition.startswith("<="):
                number = self.__try_parse_number(condition[2:])
                if isinstance(number, bool):
                    return self.__evaluation_error(result, condition, "Number not parsable (<=)")
                return result <= number

            # Check if result should be > then a number
            if condition.startswith(">"):
                number = self.__try_parse_number(condition[1:])
                if isinstance(number, bool):
                    return self.__evaluation_error(result, condition, "Number not parsable (>)")
                return result > number

            # Check if result should be < then a number
            if condition.startswith("<"):
                number = self.__try_parse_number(condition[1:])
                if isinstance(number, bool):
                    return self.__evaluation_error(result, condition, "Number not parsable (<)")
                return result < number

            # Check if result should be equal a number
            number = self.__try_parse_number(condition)
            if isinstance(number, bool):
                return self.__evaluation_error(result, condition, "Number not parsable")
            return result == number

        # Check if the condition is a number and matches the result
        if isinstance(condition, (float, int)):
            if isinstance(result, (float, int)):
                return condition == result

        return self.__evaluation_error(result, condition, "Unknown")

    def __evaluation_error(self, result, condition, throw):
        """Helper-method for easy error-logging"""
        self.log.error("Result does not match condition, dropping item."
                       " Result %s; Condition: %s; Throw: %s" %
                       (result, condition, throw))
        return False

    def __try_parse_number(self, string):
        """Try to parse a string to a number, else return False."""
        try:
            number = int(string)
        except ValueError:
            try:
                number = float(string)
            except ValueError:
                return False
        return number

    def __get_enabled_heuristics(self, url):
        """
        Get the enabled heuristics for a site, merging the default and the
        overwrite together.
        The config will only be read once and the merged site-config will be
        cached.
        """
        if url in self.__sites_heuristics:
            return self.__sites_heuristics[url]

        site = self.__sites_object[url]
        heuristics = dict(self.cfg_heuristics["enabled_heuristics"])
        if "overwrite_heuristics" in site:
            for heuristic, value in site["overwrite_heuristics"].iteritems():
                if value is False and heuristic in heuristics:
                    del heuristics[heuristic]
                else:
                    heuristics[heuristic] = value
        self.__sites_heuristics[site["url"]] = heuristics

        self.log.debug(
            "Enabled heuristics for %s: %s" % (site["url"], heuristics)
        )

        return heuristics

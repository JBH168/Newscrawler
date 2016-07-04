import logging
import os


class HeuristicsManager(object):
    """
    This class is for managing the heuristics of
    a heuristics file (../heuristics.py)
    and adding the methods needed to check the heuristic (is_article).

    The heuristics file must inherit this class.

    The config is provided in self.cfg_heuristics,
    and logging is provided in self.log.
    """
    cfg_heuristics = None
    log = None
    helper = None

    __sites_object = {}
    __sites_heuristics = {}
    __test_file = None

    def __init__(self, cfg_heuristics, sites_object, helper):
        self.cfg_heuristics = cfg_heuristics
        for site in sites_object:
            self.__sites_object[site["url"]] = site
        self.log = logging.getLogger(__name__)
        self.helper = helper

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

        test_file = None
        if self.cfg_heuristics["testing"]:
            test_file = self.__get_test_file(url)
            test_result = []

        heuristics = self.__get_enabled_heuristics(url)

        is_article = True
        self.log.info("Checking site: %s", response.url)

        for heuristic, condition in heuristics.iteritems():
            heuristic_func = getattr(self, heuristic)
            result = heuristic_func(response, site)
            if self.cfg_heuristics["testing"]:
                if isinstance(result, basestring):
                    test_result.append('"' + result.replace('"', '\\"') + '"')
                elif isinstance(result, bool):
                    r = "1" if result else "0"
                    test_result.append(r)
                else:
                    test_result.append(str(result))
            check = self.__evaluate_result(result, condition)
            is_article = check and is_article
            self.log.info("Checking heuristic (%s)"
                          " result (%s) on condition (%s): %s",
                          heuristic, result, condition, check)

        if self.cfg_heuristics["testing"]:
            test_result.append('"' + response.url + '"')
            with open(test_file, "a") as f:
                f.write(",".join(test_result) + "\r\n")
        self.log.info("Article accepted: %s", is_article)
        if self.cfg_heuristics["testing"]:
            self.log.info("Article not passed to pipeline due to testing.")
            return False
        return is_article

    def __get_test_file(self, url):
        if self.__test_file is not None:
            return self.__test_file

        replaced_site = self.helper.url_extractor.get_allowed_domains(url)
        self.__test_file = \
            self.cfg_heuristics["testing_file"].replace("%site", replaced_site)

        self.log.debug("Creating test-file %s",
                       self.__test_file)
        if os.path.isfile(self.__test_file):
            os.remove(self.__test_file)

        heuristics = self.__get_enabled_heuristics(url)

        heuristics_string = ''
        for heuristic, condition in heuristics.iteritems():
            heuristics_string += '"' + heuristic + '",'

        if not os.path.exists(os.path.dirname(self.__test_file)):
            try:
                os.makedirs(os.path.dirname(self.__test_file))
            except OSError as exc:
                self.log.error(exc)
        with open(self.__test_file, "w") as f:
            f.write(heuristics_string + '"article"\r\n')
        return self.__test_file

    def __evaluate_result(self, result, condition):
        """
        Evaluates a result of a heuristic
        with the condition given in the config

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
                    self.log.debug("Condition %s recognized as string.",
                                   condition)
                    return result == condition[1:-1]
                return self.__evaluation_error(
                    result, condition, "Result not string")

            # Only number-comparision following
            if not isinstance(result, (float, int)):
                return self.__evaluation_error(
                    result, condition, "Result not number on comparision")

            # Check if result should match a number
            if condition.startswith("="):
                number = self.__try_parse_number(condition[1:])
                if isinstance(number, bool):
                    return self.__evaluation_error(
                        result, condition, "Number not parsable (=)")
                return result == number

            # Check if result should be >= then a number
            if condition.startswith(">="):
                number = self.__try_parse_number(condition[2:])
                if isinstance(number, bool):
                    return self.__evaluation_error(
                        result, condition, "Number not parsable (>=)")
                return result >= number

            # Check if result should be <= then a number
            if condition.startswith("<="):
                number = self.__try_parse_number(condition[2:])
                if isinstance(number, bool):
                    return self.__evaluation_error(
                        result, condition, "Number not parsable (<=)")
                return result <= number

            # Check if result should be > then a number
            if condition.startswith(">"):
                number = self.__try_parse_number(condition[1:])
                if isinstance(number, bool):
                    return self.__evaluation_error(
                        result, condition, "Number not parsable (>)")
                return result > number

            # Check if result should be < then a number
            if condition.startswith("<"):
                number = self.__try_parse_number(condition[1:])
                if isinstance(number, bool):
                    return self.__evaluation_error(
                        result, condition, "Number not parsable (<)")
                return result < number

            # Check if result should be equal a number
            number = self.__try_parse_number(condition)
            if isinstance(number, bool):
                return self.__evaluation_error(
                    result, condition, "Number not parsable")
            return result == number

        # Check if the condition is a number and matches the result
        if isinstance(condition, (float, int)):
            if isinstance(result, (float, int)):
                return condition == result

        return self.__evaluation_error(result, condition, "Unknown")

    def __evaluation_error(self, result, condition, throw):
        """Helper-method for easy error-logging"""
        self.log.error("Result does not match condition, dropping item. "
                       "Result %s; Condition: %s; Throw: %s",
                       result, condition, throw)
        return False

    def __try_parse_number(self, string):
        """Try to parse a string to a number, else return False."""
        try:
            return int(string)
        except ValueError:
            try:
                return float(string)
            except ValueError:
                return False

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

        if not self.cfg_heuristics["testing"] and "overwrite_heuristics" in site:
            for heuristic, value in site["overwrite_heuristics"].iteritems():
                if value is False and heuristic in heuristics:
                    del heuristics[heuristic]
                else:
                    heuristics[heuristic] = value
        self.__sites_heuristics[site["url"]] = heuristics

        self.log.debug(
            "Enabled heuristics for %s: %s", site["url"], heuristics
        )

        return heuristics

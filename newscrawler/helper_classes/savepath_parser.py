"""
helper class for parsing the in the config defined savepath
"""
import os
import time
import re
import hashlib

from url_extractor import UrlExtractor


class SavepathParser(object):
    """
    This class contains methods to parse the given savepath
    """
    helper = None
    cfg_savepath = None
    cfg_file_path = None

    def __init__(self, cfg_savepath, cfg_file_path, helper):
        self.helper = helper

        # this part can be replaced right now; no need to replace it over and
        # over every time get_savepath is called
        timestamp_execution = int(time.time())

        # lambda is used for lazy evalutation
        cfg_savepath = re.sub(r'%time_execution\(([^\)]+)\)',
                              lambda match: self.time_replacer
                              (match, timestamp_execution), cfg_savepath)
        cfg_savepath = re.sub(r'%timestamp_execution',
                              str(timestamp_execution), cfg_savepath)
        self.cfg_savepath = cfg_savepath

        self.cfg_file_path = cfg_file_path

    @staticmethod
    def time_replacer(match, timestamp):
        """
        returns the timestamp formated with strftime the way the regex-match
        within the first set of braces defines
        """
        # match.group(0) = entire match
        # match.group(1) = match in braces #1
        return time.strftime(match.group(1), time.gmtime(timestamp))

    @staticmethod
    def append_md5_if_too_long(component, size):
        if len(component) > size:
            if size > 32:
                component_size = size - 32 - 1
                return component[:component_size] + '_' + \
                    hashlib.md5(component).hexdigest()
            else:
                return hashlib.md5(component).hexdigest()[:size]
        else:
            return component

    def get_savepath(self, url):
        """
        returns the evaluated savepath for the given url
        """
        timestamp = int(time.time())

        savepath = self.cfg_savepath

        # lambda is used for lazy evalutation
        savepath = re.sub(r'%time_download\(([^\)]+)\)',
                          lambda match: SavepathParser.time_replacer(
                              match, timestamp), savepath)
        savepath = re.sub(r'%timestamp_download', str(timestamp), savepath)

        savepath = re.sub(r'%domain\(([^\)]+)\)',
                          lambda match: UrlExtractor
                          .get_allowed_domains_without_subdomains(url)[
                              :int(match.group(1))], savepath)
        savepath = re.sub(r'%appendmd5_domain\(([^\)]+)\)',
                          lambda match: SavepathParser.append_md5_if_too_long(
                              UrlExtractor
                              .get_allowed_domains_without_subdomains(url),
                              int(match.group(1))), savepath)
        savepath = re.sub(r'%md5_domain\(([^\)]+)\)',
                          lambda match: hashlib.md5(
                              UrlExtractor
                              .get_allowed_domains_without_subdomains(url))
                          .hexdigest()[:int(match.group(1))], savepath)

        savepath = re.sub(r'%full_domain\(([^\)]+)\)',
                          lambda match: UrlExtractor.get_allowed_domains(url)[
                              :int(match.group(1))], savepath)
        savepath = re.sub(r'%appendmd5_full_domain\(([^\)]+)\)',
                          lambda match: SavepathParser.append_md5_if_too_long(
                              UrlExtractor.get_allowed_domains(url),
                              int(match.group(1))), savepath)
        savepath = re.sub(r'%md5_full_domain\(([^\)]+)\)',
                          lambda match: hashlib.md5(
                              UrlExtractor.get_allowed_domains(url))
                          .hexdigest()[:int(match.group(1))], savepath)

        savepath = re.sub(r'%subdomains\(([^\)]+)\)',
                          lambda match: UrlExtractor.get_subdomains(url)[
                              :int(match.group(1))], savepath)
        savepath = re.sub(r'%appendmd5_subdomains\(([^\)]+)\)',
                          lambda match: SavepathParser.append_md5_if_too_long(
                              UrlExtractor.get_subdomains(url),
                              int(match.group(1))), savepath)
        savepath = re.sub(r'%md5_subdomains\(([^\)]+)\)',
                          lambda match: hashlib.md5(
                              UrlExtractor.get_subdomains(url))
                          .hexdigest()[:int(match.group(1))], savepath)

        savepath = re.sub(r'%url_directory_string\(([^\)]+)\)',
                          lambda match: UrlExtractor
                          .get_url_directory_string(url)[:int(match.group(1))],
                          savepath)
        savepath = re.sub(r'%appendmd5_url_directory_string\(([^\)]+)\)',
                          lambda match: SavepathParser.append_md5_if_too_long(
                              UrlExtractor.get_url_directory_string(url),
                              int(match.group(1))), savepath)
        savepath = re.sub(r'%md5_url_directory_string\(([^\)]+)\)',
                          lambda match: hashlib.md5(
                              UrlExtractor.get_url_directory_string(url))
                          .hexdigest()[:int(match.group(1))], savepath)

        savepath = re.sub(r'%url_file_name\(([^\)]+)\)',
                          lambda match: UrlExtractor
                          .get_url_file_name(url)[:int(match.group(1))],
                          savepath)
        savepath = re.sub(r'%md5_url_file_name\(([^\)]+)\)',
                          lambda match: hashlib.md5(
                              UrlExtractor.get_url_file_name(url))
                          .hexdigest()[:int(match.group(1))], savepath)

        abs_savepath = self.get_abs_path(savepath)

        savepath = re.sub(r'%max_url_file_name',
                          lambda match: UrlExtractor.get_url_file_name(url)[
                              :SavepathParser.get_max_url_file_name_length(
                                  abs_savepath)], savepath)
        savepath = re.sub(r'%appendmd5_max_url_file_name',
                          lambda match: SavepathParser.append_md5_if_too_long(
                              UrlExtractor.get_url_file_name(url),
                              SavepathParser.get_max_url_file_name_length(
                                  abs_savepath)), savepath)

        # ensure the savepath doesn't contain any invalid characters
        return SavepathParser.remove_not_allowed_chars(savepath)

    @staticmethod
    def remove_not_allowed_chars(savepath):
        """
        returns the given savepath without invalid savepath characters
        """
        split_savepath = os.path.splitdrive(savepath)
        # https://msdn.microsoft.com/en-us/library/aa365247.aspx
        savepath_without_invalid_chars = re.sub(r'<|>|:|\"|\||\?|\*', '_',
                                                split_savepath[1])
        return split_savepath[0] + savepath_without_invalid_chars

    @staticmethod
    def get_abs_path_static(savepath, cfg_file_path):
        """
        returns an absolute version of savepath
        relative paths are relative to the config file
        """
        if os.path.isabs(savepath):
            return os.path.abspath(savepath)
        else:
            return os.path.abspath(
                os.path.join(os.path.dirname(cfg_file_path), (savepath))
                )

    def get_abs_path(self, savepath):
        """
        returns an absolute version of savepath
        relative paths are relative to the config file
        """
        return self.get_abs_path_static(savepath, self.cfg_file_path)

    @staticmethod
    def get_base_path(path):
        """
        Returns the path until the first %
        So
        /this/is/a/pa%th would become /this/is/a

        :param path: String, the path to get the base from
        """
        if "%" not in path:
            return path

        path = os.path.split(path)[0]

        while "%" in path:
            path = os.path.split(path)[0]

        return path

    @staticmethod
    def get_max_url_file_name_length(savepath):
        """
        returns the first max. allowed number of chars of the url_file_name
        """
        number_occurrences = savepath.count('%max_url_file_name')
        number_occurrences += savepath.count('%appendmd5_max_url_file_name')

        savepath_copy = savepath
        size_without_max_url_file_name = len(
            savepath_copy.replace('%max_url_file_name', '')
            .replace('%appendmd5_max_url_file_name', '')
            )

        # Windows: max file path length is 260 characters including
        # NULL (string end)
        max_size = 260 - 1 - size_without_max_url_file_name
        max_size_per_occurrence = max_size / number_occurrences

        return max_size_per_occurrence

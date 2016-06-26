"""
helper class for parsing the in the config defined savepath
"""


import re
import time
import hashlib
import os
from url_extractor import url_extractor

class savepath_parser(object):
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

    def get_savepath(self, url):
        """
        returns the evaluated savepath for the given url
        """
        timestamp = int(time.time())

        savepath = self.cfg_savepath

        # lambda is used for lazy evalutation
        savepath = re.sub(r'%time_download\(([^\)]+)\)',
                          lambda match: savepath_parser.time_replacer(match, timestamp),
                          savepath)
        savepath = re.sub(r'%timestamp_download', str(timestamp), savepath)
        savepath = re.sub(r'%domain',
                          lambda match: url_extractor
                          .get_allowed_domains_without_subdomains(url),
                          savepath)
        savepath = re.sub(r'%md5_domain\(([^\)]+)\)',
                          lambda match: hashlib.md5(url_extractor.get_allowed_domains_without_subdomains(url))
                          .hexdigest()[:match], savepath)
        savepath = re.sub(r'%full_domain',
                          lambda match: url_extractor.get_allowed_domains(url), savepath)
        savepath = re.sub(r'%url_directory_string\(([^\)]+)\)',
                          lambda match: url_extractor
                          .get_url_directory_string(url)[:match], savepath)
        savepath = re.sub(r'%url_file_name\(([^\)]+)\)',
                          lambda match: url_extractor
                          .get_url_file_name(url)[:match], savepath)
        savepath = re.sub(r'%md5_url_file_name\(([^\)]+)\)',
                          lambda match: hashlib.md5(url_extractor.get_url_file_name(url))
                          .hexdigest()[:match], savepath)

        savepath = self.get_abs_path(savepath)

        savepath = re.sub(r'%max_url_file_name',
                          lambda match: savepath_parser.get_max_url_file_name(savepath,
                                                                   url),
                          savepath)

        # ensure the savepath doesn't contain any invalid characters
        return savepath_parser.remove_not_allowed_chars(savepath)

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

    def get_abs_path(self, savepath):
        """
        returns an absolute version of savepath
        relative paths are relative to the config file
        """
        if os.path.isabs(savepath):
            return os.path.abspath(savepath)
        else:
            return os.path.abspath(os.path.join(os.path.dirname
                                                (self.cfg_file_path),
                                                (savepath)))

    @staticmethod
    def get_max_url_file_name(savepath, url):
        """
        returns the first max. allowed number of chars of the url_file_name
        """
        number_occurrences = savepath.count('%max_url_file_name')
        savepath_copy = savepath
        size_without_max_url_file_name = len(savepath_copy
                                             .replace('%max_url_file_name',
                                                      ''))
        # Windows: max file path length is 260 characters including
        # NULL (string end)
        max_size = 260 - 1 - size_without_max_url_file_name
        max_size_per_occurrence = max_size / number_occurrences

        return url_extractor \
            .get_url_file_name(url)[:max_size_per_occurrence]

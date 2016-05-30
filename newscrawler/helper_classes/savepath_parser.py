import re
import time
import hashlib
import os


class savepath_parser(object):
    helper = None
    cfg_savepath = None
    cfg_file_path = None

    def __init__(self, cfg_savepath, cfg_file_path, helper):
        self.helper = helper

        timestamp_execution = int(time.time())
        cfg_savepath = re.sub(r'%time_execution\(([^\)]+)\)',
                              lambda match: self.time_replacer
                              (match, timestamp_execution), cfg_savepath)
        cfg_savepath = re.sub(r'%timestamp_execution',
                              str(timestamp_execution), cfg_savepath)
        self.cfg_savepath = cfg_savepath

        self.cfg_file_path = cfg_file_path

    def time_replacer(self, match, timestamp):
        # match.group(0) = entire match
        # match.group(1) = match in braces #1
        return time.strftime(match.group(1), time.gmtime(timestamp))

    def get_savepath(self, url):
        timestamp = int(time.time())

        savepath = self.cfg_savepath

        savepath = re.sub(r'%time_download\(([^\)]+)\)',
                          lambda match: self.time_replacer(match, timestamp),
                          savepath)
        savepath = re.sub(r'%timestamp_download', str(timestamp), savepath)
        savepath = re.sub(r'%domain',
                          lambda match: self.helper.url_extractor
                          .get_allowed_domains_without_subdomains(url),
                          savepath)
        savepath = re.sub(r'%md5_domain\(([^\)]+)\)',
                          lambda match: hashlib.md5(self.helper
                          .url_extractor
                          .get_allowed_domains_without_subdomains(url))
                          .hexdigest()[:match], savepath)
        savepath = re.sub(r'%full_domain',
                          lambda match: self.helper.url_extractor
                          .get_allowed_domains(url), savepath)
        savepath = re.sub(r'%url_directory_string\(([^\)]+)\)',
                          lambda match: self.helper.url_extractor
                          .get_url_directory_string(url)[:match], savepath)
        savepath = re.sub(r'%url_file_name\(([^\)]+)\)',
                          lambda match: self.helper.url_extractor
                          .get_url_file_name(url)[:match], savepath)
        savepath = re.sub(r'%md5_url_file_name\(([^\)]+)\)',
                          lambda match: hashlib.md5(self.helper
                          .url_extractor.get_url_file_name(url))
                          .hexdigest()[:match], savepath)

        savepath = self.get_abs_path(savepath)

        savepath = re.sub(r'%max_url_file_name',
                          lambda match: self.get_max_url_file_name(savepath,
                                                                   url),
                          savepath)

        return savepath

    def get_abs_path(self, savepath):
        if os.path.isabs(savepath):
            return os.path.abspath(savepath)
        else:
            return os.path.abspath(os.path.join(os.path.dirname
                                                (self.cfg_file_path),
                                                (savepath)))

    def get_max_url_file_name(self, savepath, url):
        number_occurrences = savepath.count('%max_url_file_name')
        savepath_copy = savepath
        size_without_max_url_file_name = len(savepath_copy
                                             .replace('%max_url_file_name',
                                                      ''))
        max_size = 260 - 1 - size_without_max_url_file_name
        max_size_per_occurrence = max_size / number_occurrences

        return self.helper.url_extractor \
            .get_url_file_name(url)[:max_size_per_occurrence]

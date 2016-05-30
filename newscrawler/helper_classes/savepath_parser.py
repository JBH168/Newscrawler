import re
import time


class savepath_parser(object):
    helper = None
    cfg_savepath = None

    def __init__(self, cfg_savepath, helper):
        self.helper = helper

        timestamp_execution = int(time.time())
        cfg_savepath = re.sub(r'%time_execution\(([^\)]+)\)',
                              lambda match: self.time_replacer
                              (match, timestamp_execution), cfg_savepath)
        cfg_savepath = re.sub(r'%timestamp_execution',
                              str(timestamp_execution), cfg_savepath)
        self.cfg_savepath = cfg_savepath

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
                          .get_allowed_domains_without_subdomains(url), savepath)
        savepath = re.sub(r'%full_domain',
                          lambda match: self.helper.url_extractor
                          .get_allowed_domains(url), savepath)
        savepath = re.sub(r'%url_directory_string',
                          lambda match: self.helper.url_extractor
                          .get_url_directory_string(url), savepath)
        savepath = re.sub(r'%url_file_name',
                          lambda match: self.helper.url_extractor
                          .get_url_file_name(url), savepath)

        return savepath

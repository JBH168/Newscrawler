import os
import re
import time


class download(object):
    cfg_savepath = None
    timestamp_execution = None
    savepath_dict = {"timestamp_execution": "self.timestamp_execution",
                     "timestamp_download": "int(time.time())",
                     "domain": "",
                     "full_domain": "",
                     "directory_string": "",
                     "file_name": ""}

    def __init__(self, cfg_savepath):
        timestamp_execution = int(time.time())
        cfg_savepath = re.sub(r'%time_execution\(([^\)]+)\)',
                              self.time_replacer, cfg_savepath)
        for item in self.savepath_dict.keys():
            cfg_savepath = re.sub(r'%' + item, r'{' + item + '}', cfg_savepath)
        self.cfg_savepath = cfg_savepath

    def time_replacer(self, match):
        # match.group(0) = entire match
        # match.group(1) = match in braces #1
        return time.strftime(match.group(1))

    def save_webpage(self, response):
        filename = self.get_filename(response)

        # TODO: catch errors
        # like too long file names
        with open(self.get_abs_file_path(filename), 'wb') as file:
            file.write(response.body)
        file.close()

    def get_filename(self, response):
        filename = response.url.split("/")[-1]

        if not filename:  # empty string
            filename = response.url.split("/")[-2]

        if not filename.endswith(".html"):
            filename = filename + ".html"

        return filename

    def get_abs_file_path(self, filename):
        # for the following three lines of code, see:
        # http://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
        #
        # may be replaced with a file path given in a json file
        script_dir = os.path.dirname(__file__)  # absolute dir the script is in
        rel_path = "../../data/" + filename
        abs_file_path = os.path.abspath(os.path.join(script_dir, rel_path))

        # ensure the directory actually exists, if it doesn't, create it
        abs_dir = os.path.dirname(abs_file_path)
        if not os.path.exists(abs_dir):
            os.makedirs(abs_dir)

        return abs_file_path

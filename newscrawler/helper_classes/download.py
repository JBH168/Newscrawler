import os

import logging


class download(object):
    helper = None

    log = logging.getLogger(__name__)

    def __init__(self, helper):
        self.helper = helper

    def save_webpage(self, response):
        file_path = self.helper.savepath_parser.get_savepath(response.url)

        self.log.debug("Saving to %s" % file_path)

        self.ensure_directory_exists(file_path)

        with open(file_path, 'wb') as file_:
            file_.write(response.body)
        file_.close()

    def ensure_directory_exists(self, file_path):
        dir_ = os.path.dirname(file_path)
        if not os.path.exists(dir_):
            os.makedirs(dir_)

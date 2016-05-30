import os


class download(object):
    helper = None

    def __init__(self, helper):
        self.helper = helper

    def save_webpage(self, response):
        filename = self.get_filename(response)

        file_path = self.helper.savepath_parser.get_savepath(response.url)
        self.ensure_directory_exists(file_path)
        with open(file_path, 'wb') as file:
            file.write(response.body)
        file.close()

    def ensure_directory_exists(self, file_path):
        dir = os.path.dirname(file_path)
        if not os.path.exists(dir):
            os.makedirs(dir)

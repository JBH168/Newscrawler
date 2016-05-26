
from helper_classes.download import download
from helper_classes.heuristics import heuristics


class helper(object):

    download = None

    def __init__(self):
        self.download = download()
        self.heuristics = heuristics()

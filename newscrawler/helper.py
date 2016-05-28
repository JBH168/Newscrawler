
from helper_classes.download import download
from helper_classes.heuristics import heuristics
from helper_classes.url_extractor import url_extractor


class helper(object):

    download = None
    heuristics = None
    url_extractor = None

    def __init__(self, cfg_heuristics):
        self.download = download()
        self.heuristics = heuristics(cfg_heuristics)
        self.url_extractor = url_extractor()

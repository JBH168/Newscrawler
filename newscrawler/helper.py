
from helper_classes.download import download
from helper_classes.heuristics import heuristics
from helper_classes.url_extractor import url_extractor


class helper(object):

    download = None
    heuristics = None
    url_extractor = None

    def __init__(self, cfg_heuristics, cfg_savepath):
        self.download = download(cfg_savepath)
        self.heuristics = heuristics(cfg_heuristics)
        self.url_extractor = url_extractor()

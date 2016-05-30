
from helper_classes.download import download
from helper_classes.heuristics import heuristics
from helper_classes.url_extractor import url_extractor
from helper_classes.savepath_parser import savepath_parser


class helper(object):

    download = None
    heuristics = None
    url_extractor = None
    savepath_parser = None

    def __init__(self, cfg_heuristics, cfg_savepath):
        self.download = download()
        self.heuristics = heuristics(cfg_heuristics)
        self.url_extractor = url_extractor()
        self.savepath_parser = savepath_parser(cfg_savepath, self)

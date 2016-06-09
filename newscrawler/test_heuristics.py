import os
import sys
from helper_classes.heuristics import heuristics

from scrapy.selector import Selector


class test_heursitics(object):
    def __init__(self, root_dir):
        print "ogTest,h1,h1Linked,h2,h2Linked,h3,h3Linked,h4,h4Linked,h5,h5Linked,h6,h6Linked,hAll,hAllLinked,site,file"
        self.heuristics = heuristics(False)

        for root, dirs, files in os.walk(root_dir):
            for filename in files:
                self.test_file(root + "/" + filename, filename)
        return

    def get_file_content(self, filepath):
        # print "Reading: " + filepath
        with open(filepath, 'r') as file_:
            return file_.read().replace('\n', '')

    def test_file(self, filepath, filename):
        content = self.get_file_content(filepath)
        result = self.test_content(content)
        base_url = filepath.split('/')[12]
        r = result["linked_headlines"]
        h_all = 0
        h_all_linked = 0
        for i in range(1, 7):
            h_all += r["h%s" % i][0]
            h_all_linked += r["h%s" % i][1]
        print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
                result["og_test"],
                r["h1"][0],
                r["h1"][1],
                r["h2"][0],
                r["h2"][1],
                r["h3"][0],
                r["h3"][1],
                r["h4"][0],
                r["h4"][1],
                r["h5"][0],
                r["h5"][1],
                r["h6"][0],
                r["h6"][1],
                h_all,
                h_all_linked,
                '"' + base_url + '"',
                '"' + filename + '"'
            )

    def test_content(self, content):
        selector = Selector(text=content)
        results = {}
        results["og_type"] = self.heuristics.og_test(selector)
        results["linked_headlines"] = self.heuristics.linked_headlines(selector)
        return results

if __name__ == "__main__":
    test_heursitics(sys.argv[1])

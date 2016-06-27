from subprocess import Popen
import subprocess
import signal
import sys
import os
import time
import logging
from newscrawler.config import JsonConfig
from newscrawler.config import CrawlerConfig
from scrapy.utils.log import configure_logging
import threading

PROCESS = None


class start_processes(object):

    python_command = None
    crawlers = []
    cfg = None
    log = None
    helper = None
    cfg_file_path = None
    shall_resume = False
    threads = []
    threads_daemonized = []
    crawler_list = None
    json_file_path = None
    shutdown = False

    __single_crawler = False

    def __init__(self):
        configure_logging({"LOG_LEVEL": "CRITICAL"})
        self.log = logging.getLogger(__name__)

        self.shall_resume = len([arg for arg in sys.argv
                                 if arg == '--resume']) != 0

        # Get & set CFG and JSON locally
        self.cfg = CrawlerConfig.get_instance()
        self.cfg_file_path = self.get_config_file_path()
        self.cfg.setup(self.cfg_file_path)

        urlinput_file_path = self.cfg.section('Files')['urlinput']
        self.json_file_path = self.get_abs_file_path(
            urlinput_file_path, quit_on_error=True)

        self.json = JsonConfig.get_instance()
        self.json.setup(self.json_file_path)

        self.crawler_list = crawler_list()

        self.__single_crawler = self.get_abs_file_path("./initial.py")

    def manage_crawlers(self):
        """
        Starts a thread for each site and a crawler for it
        """
        sites = self.json.get_site_objects()
        for index, site in enumerate(sites):
            if "daemonize" in site:
                thread = threading.Thread(target=self.manage_crawler,
                                          args=(index, site["daemonize"]),
                                          kwargs={})
                self.threads_daemonized.append(thread)
                thread.start()
            else:
                self.crawler_list.appendItem(index)

        for i in range(self.cfg.section(
                'Crawler')['numberofparallelcrawlers']):
            thread = threading.Thread(target=self.manage_crawler,
                                      args=(),
                                      kwargs={})
            self.threads.append(thread)
            thread.start()

        # join alive threads
        #   1. crawler Threads
        #   2. daemonized Threads (read somewhere this might prevent zombies...
        #                          TODO: research)
        for thread in self.threads:
            thread.join()
        for thread in self.threads_daemonized:
            thread.join()

    def manage_crawler(self, index=None, daemonize=0):
        # if daemonized
        while daemonize > 0 and not self.shutdown:
            beginTime = int(time.time())
            self.start_crawler(index, daemonize)
            time.sleep(beginTime + daemonize - int(time.time()))

        # otherwise
        index = True
        while not self.shutdown and index is not None:
            index = self.crawler_list.getNextItem()
            if index is None:
                break
            self.start_crawler(index)

    def start_crawler(self, index, daemonize=0):
        """
        Starts a crawler from the input-array

        :param index: The array-index of the site
        """
        python = self.get_python_command()
        call_process = [python,
                        self.__single_crawler,
                        self.cfg_file_path,
                        self.json_file_path,
                        "%s" % index,
                        "%s" % self.shall_resume,
                        "%s" % daemonize]

        self.log.debug("Calling Process: %s" % call_process)

        crawler = Popen(call_process,
                        stderr=None,
                        stdout=None)
        crawler.communicate()
        self.crawlers.append(crawler)

    def get_python_command(self):
        """
        Get the correct command for executing python2.7

        :return string: python or python2.7
        """
        if self.python_command is not None:
            return self.python_command

        string = "python2.7"
        try:
            self.__get_python(string)
        except OSError:
            string = "python"
            output = self.__get_python(string)
            if not output.startswith("Python 2.7"):
                print "ERROR: You need to have Python 2.7.* installed " \
                      "and in your PATH. It must be executable by invoking " \
                      "python or python2.7."
                sys.exit(1)
        self.python_command = string
        return string

    def graceful_stop(self):
        """
        This function will be called when a graceful-stop is initiated
        """
        self.shutdown = True
        return True

    def get_config_file_path(self):
        """
        returns the config file path
         - if passed to this script, ensures it's a valid file path
         - if not passed to this script or not valid, falls back to the
           standard ./newscrawler.cfg
        """
        # test if the config file path was passed to this script
        # argv[0] should be this script's name
        # argv[1] should be the config file path
        #   for path names with spaces, use "path"
        if len(sys.argv) > 1:
            input_config_file_path = os.path.abspath(sys.argv[1])

            if os.path.exists(input_config_file_path) and os.path.splitext(
                    input_config_file_path)[1] == ".cfg":
                return input_config_file_path
            else:
                self.log.error("First argument passed to initial.py is not"
                               " the config file. Falling back to"
                               " ./newscrawler.cfg.")

        # Default
        return self.get_abs_file_path("./newscrawler.cfg", quit_on_error=True)

    def __get_python(self, string):
        return Popen([string, "--version"],
                     stderr=subprocess.STDOUT,
                     stdout=subprocess.PIPE).communicate()[0]

    # TODO: move into a helper class; copy in initial.py
    def get_abs_file_path(self, rel_file_path, quit_on_error=None):
        """
        returns the absolute file path of the given relative file path
        to either this script or to the config file.

        May throw a RuntimeError if quit_on_error is True
        """
        if self.cfg_file_path is not None and \
                not self.cfg.section('General')['relativetoinitial']:
            script_dir = os.path.dirname(self.cfg_file_path)
        else:
            # absolute dir this script is in
            script_dir = os.path.dirname(__file__)

        abs_file_path = os.path.abspath(
            os.path.join(script_dir, rel_file_path))

        if not os.path.exists(abs_file_path):
            self.log.error(abs_file_path + " does not exist.")
            if quit_on_error is True:
                raise RuntimeError("Importet file not found. Quit.")

        return abs_file_path


class crawler_list(object):
    lock = None
    crawler_list = []

    def __init__(self):
        self.lock = threading.Lock()

    def appendItem(self, item):
        self.lock.acquire()
        try:
            self.crawler_list.append(item)
        finally:
            self.lock.release()

    def getNextItem(self):
        self.lock.acquire()
        try:
            if len(self.crawler_list) > 0:
                item = self.crawler_list.pop(0)
            else:
                item = None
        finally:
            self.lock.release()
            return item


def graceful_stop(a, b):
    if PROCESS is not None:
        PROCESS.graceful_stop()


signal.signal(signal.SIGTERM, graceful_stop)
signal.signal(signal.SIGABRT, graceful_stop)
signal.signal(signal.SIGINT, graceful_stop)

if __name__ == "__main__":
    PROCESS = start_processes()
    PROCESS.manage_crawlers()

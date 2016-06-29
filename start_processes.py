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
    daemon_list = None
    json_file_path = None
    shutdown = False

    __single_crawler = False

    def __init__(self):
        configure_logging({"LOG_LEVEL": "CRITICAL"})
        self.log = logging.getLogger(__name__)

        if len(sys.argv) > 1 and (sys.argv[1] == 'help' or
                                  sys.argv[1] == '--help' or
                                  sys.argv[1] == '?'):
            self.print_help()
            sys.exit(0)

        self.shall_resume = self.has_arg('--resume')

        if self.has_arg('--reset-db'):
            self.cleanup_db()
        # elif self.has_arg('--reset-files'):
        #     self.cleanup_files()
        # elif self.has_arg('--reset'):
        #     self.cleanup_db()
        #     self.cleanup_files()

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
        self.daemon_list = daemon_list()

        self.__single_crawler = self.get_abs_file_path("./initial.py")

    def has_arg(self, string):
        return len([arg for arg in sys.argv if arg == string]) != 0

    def manage_crawlers(self):
        """
        Starts a thread for each site and a crawler for it
        """
        sites = self.json.get_site_objects()
        for index, site in enumerate(sites):
            if "daemonize" in site:
                self.daemon_list.addDaemon(index, site["daemonize"])
            else:
                self.crawler_list.appendItem(index)

        num_threads = self.cfg.section('Crawler')['numberofparallelcrawlers']
        if self.crawler_list.len() < num_threads:
            num_threads = self.crawler_list.len()

        for i in range(num_threads):
            thread = threading.Thread(target=self.manage_crawler,
                                      args=(),
                                      kwargs={})
            self.threads.append(thread)
            thread.start()

        num_daemons = self.cfg.section('Crawler')['numberofparalleldaemons']
        if self.daemon_list.len() < num_daemons:
            num_daemons = self.daemon_list.len()

        for i in range(num_daemons):
            thread_daemonized = threading.Thread(target=self.manage_daemon,
                                                 args=(),
                                                 kwargs={})
            self.threads_daemonized.append(thread_daemonized)
            thread_daemonized.start()

        # join alive threads
        #   1. crawler Threads
        #   2. daemonized Threads (read somewhere this might prevent zombies...
        #                          TODO: research)
        for thread in self.threads:
            thread.join()
        for thread in self.threads_daemonized:
            thread.join()

    def manage_crawler(self):
        index = True
        while not self.shutdown and index is not None:
            index = self.crawler_list.getNextItem()
            if index is None:
                break
            self.start_crawler(index)

    def manage_daemon(self):
        while not self.shutdown:
            # next scheduled daemon, tuple (time, index)
            item = self.daemon_list.getNextItem()
            cur = time.time()
            if cur < item[0]:
                time.sleep(item[0] - cur)
            self.start_crawler(item[1])

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

    def print_help(self):
        _help = \
            """
        CColon Newscrawler
        ------------------


Usage:

    %s %s [help] [cfg_file_path] [arg] ...



Arguments:

    help          : '--help' | 'help' | '?' prints this help message and exits

    cfg_file_path : absolute or relative file path to the config file

    arg ...       : arguments passed to this script
                --resume        Resume crawling from last crawl
                --reset-db      Reset the Database
            """
        print _help % (self.get_python_command(), __file__)

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

    def cleanup_db(self):
        pass  # TODO: implement


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

    def len(self):
        return len(self.crawler_list)

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


class daemon_list(object):
    lock = None

    daemons = {}
    queue = []
    queue_times = []

    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def sortQueue(self):
        self.queue = sorted(self.queue, key=lambda t: t[0])
        self.queue_times = sorted(self.queue_times)

    def len(self):
        return len(self.daemons)

    def addDaemon(self, index, _time):
        self.lock.acquire()
        try:
            self.daemons[index] = _time
            self.addExecution(time.time(), index)
        finally:
            self.lock.release()

    def addExecution(self, _time, index):
        _time = int(_time)
        while _time in self.queue_times:
            _time += 1

        self.queue_times.append(_time)
        self.queue.append((_time, index))

    def getNextItem(self):
        self.lock.acquire()
        self.sortQueue()
        try:
            item = self.queue.pop(0)
            self.queue_times.pop(0)
            self.addExecution(time.time() + self.daemons[item[1]], item[1])
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

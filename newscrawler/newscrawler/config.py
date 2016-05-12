# -*- coding: utf-8 -*-
"""
This is the config-loading module which loads by default the config in the
root-folder of the project.
It handles the [General]-Section of the config.

It loads the newscrawler.cfg and parses it with the config-parser-module.
"""

import logging

import ConfigParser


class CrawlerConfig(object):
    """The actual class. First parameter: config-file."""

    log = None
    log_output = []

    def __init__(self, filepath):
        self.log = logging.getLogger(__name__)
        self.cfg = ConfigParser.RawConfigParser()
        self.cfg.read(filepath)
        self.sections = self.cfg.sections()
        self.log_output.append(
            {"level": "info", "msg": "Loading config-file (%s)" % filepath})
        self.load_config()
        self.handle_general()

    def load_config(self):
        """Load the config to self.config. Recursive dict:
           [section][option] = value"""
        self.config = {}

        # Parse sections, its options and put it in self.config.
        for section in self.sections:

            self.config[section] = {}
            options = self.cfg.options(section)

            # Parse options of each section
            for option in options:

                try:
                    self.config[section][option] = self.cfg \
                        .get(section, option)
                    if self.config[section][option] == -1:
                        self.log_output.append(
                            {"level": "debug", "msg": "Skipping: %s" % option})
                except ConfigParser.NoOptionError as exc:
                    self.log_output.append(
                        {"level": "error",
                         "msg": "Exception on %s: %s" % (option, exc)})
                    self.config[section][option] = None

    def handle_general(self):
        """Handle the General-section of the config."""
        self.log.setLevel(self.config["General"]["loglevel"])
        logging.basicConfig(format=self.config["General"]["logformat"])

        # Now, after log-level is correctly set, lets log them.
        for msg in self.log_output:
            if msg["level"] is "error":
                self.log.error(msg["msg"])
            elif msg["level"] is "info":
                self.log.info(msg["msg"])
            elif msg["level"] is "debug":
                self.log.debug(msg["msg"])


if __name__ == "__main__":
    CrawlerConfig("/home/moritz/documents/Uni/Vorlesungen/SWP/"
                  "ccolon_newscrawler/newscrawler/newscralwer.cfg")

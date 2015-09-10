# Copyright (c) 2015 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of kiwi.
#
# kiwi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kiwi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kiwi.  If not, see <http://www.gnu.org/licenses/>
#
import logging
import sys


class LoggerSchedulerFilter(logging.Filter):
    def filter(self, record):
        # messages from apscheduler scheduler instances are filtered out
        # they conflict with console progress information
        ignorables = [
            'apscheduler.scheduler',
            'apscheduler.executors.default'
        ]
        return record.name not in ignorables


class InfoFilter(logging.Filter):
    def filter(self, record):
        # only messages with record level INFO, WARNING and DEBUG can pass
        # for messages with another level an extra handler is used
        return record.levelno in (
            logging.INFO, logging.WARNING, logging.DEBUG
        )


class Logger(logging.Logger):
    """
        kiwi logging facility based on python logging
    """
    def __init__(self, name):
        logging.Logger.__init__(self, name)

        formatter = logging.Formatter('%(levelname)s: %(message)s')

        # log INFO, WARNING and DEBUG messages to stdout
        console_info = logging.StreamHandler(sys.__stdout__)
        console_info.setFormatter(formatter)
        console_info.addFilter(InfoFilter())
        console_info.addFilter(LoggerSchedulerFilter())

        # log ERROR messages to stderr (default stream)
        console_error = logging.StreamHandler()
        console_error.setLevel(logging.ERROR)
        console_error.setFormatter(formatter)

        self.addHandler(console_info)
        self.addHandler(console_error)

    def progress(self, current, total, prefix, bar_length=40):
        try:
            percent = float(current) / total
        except Exception:
            # we don't want the progress to raise an exception
            # In case of any error e.g division by zero the current
            # way out is to skip the progress update
            return
        hashes = '#' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\r{0}: [{1}] {2}%".format(
            prefix, hashes + spaces, int(round(percent * 100))
        ))
        sys.stdout.flush()


def init(level=logging.INFO):
    global log
    logging.setLoggerClass(Logger)
    log = logging.getLogger("kiwi")
    log.setLevel(level)

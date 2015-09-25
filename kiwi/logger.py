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

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': WHITE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
    'RED': RED,
    'GREEN': GREEN,
    'YELLOW': YELLOW,
    'BLUE': BLUE,
    'MAGENTA': MAGENTA,
    'CYAN': CYAN,
    'WHITE': WHITE
}

RESET_SEQ = '\033[0m'
COLOR_SEQ = '\033[3;%dm'
COLOR_LIGHT_SEQ = '\033[2;%dm'
BOLD_SEQ = '\033[1m'


class ColorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname
        color_norm = COLOR_SEQ % (30 + COLORS[levelname])
        color_light = COLOR_LIGHT_SEQ % (30 + COLORS[levelname])
        message = logging.Formatter.format(self, record)
        message = message.replace(
            '$RESET', RESET_SEQ
        ).replace(
            '$BOLD', BOLD_SEQ
        ).replace(
            '$COLOR', color_norm
        ).replace(
            '$LIGHTCOLOR', color_light
        )
        for k, v in COLORS.items():
            message = message.replace(
                '$' + k, COLOR_SEQ % (v + 30)
            ).replace(
                '$BG' + k, COLOR_SEQ % (v + 40)
            ).replace(
                '$BG-' + k, COLOR_SEQ % (v + 40)
            )
        return message + RESET_SEQ


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
        # only messages with record level INFO and WARNING can pass
        # for messages with another level an extra handler is used
        return record.levelno in (
            logging.INFO, logging.WARNING
        )


class DebugFilter(logging.Filter):
    def filter(self, record):
        # only messages with record level DEBUG can pass
        # for messages with another level an extra handler is used
        if record.levelno == logging.DEBUG:
            return True


class ErrorFilter(logging.Filter):
    def filter(self, record):
        # only messages with record level DEBUG can pass
        # for messages with another level an extra handler is used
        if record.levelno == logging.ERROR:
            return True


class Logger(logging.Logger):
    """
        kiwi logging facility based on python logging
    """
    def __init__(self, name):
        logging.Logger.__init__(self, name)

        # log INFO and WARNING messages to stdout
        console_info = logging.StreamHandler(sys.__stdout__)
        console_info.setFormatter(
            ColorFormatter('%(levelname)s: %(message)s')
        )
        console_info.addFilter(InfoFilter())
        console_info.addFilter(LoggerSchedulerFilter())

        # log DEBUG messages to stdout
        console_debug = logging.StreamHandler(sys.__stdout__)
        console_debug.setFormatter(
            ColorFormatter('$LIGHTCOLOR%(levelname)s: %(message)s')
        )
        console_debug.addFilter(DebugFilter())

        # log ERROR messages to stderr
        console_error = logging.StreamHandler(sys.__stderr__)
        console_error.setFormatter(
            ColorFormatter('$COLOR%(levelname)s: %(message)s')
        )
        console_error.addFilter(ErrorFilter())

        self.addHandler(console_info)
        self.addHandler(console_error)
        self.addHandler(console_debug)

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

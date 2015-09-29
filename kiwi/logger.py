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


class ColorMessage(object):
    def __init__(self):
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
        self.color = {
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
        self.esc = {
            'reset': '\033[0m',
            'color': '\033[3;%dm',
            'color_light': '\033[2;%dm',
            'bold': '\033[1m'
        }

    def format_message(self, level, message):
        message = message.replace(
            '$RESET',
            self.esc['reset']
        ).replace(
            '$BOLD',
            self.esc['bold']
        ).replace(
            '$COLOR',
            self.esc['color'] % (30 + self.color[level])
        ).replace(
            '$LIGHTCOLOR',
            self.esc['color_light'] % (30 + self.color[level])
        )
        for color_name, color_id in self.color.items():
            message = message.replace(
                '$' + color_name,
                self.esc['color'] % (color_id + 30)
            ).replace(
                '$BG' + color_name,
                self.esc['color'] % (color_id + 40)
            ).replace(
                '$BG-' + color_name,
                self.esc['color'] % (color_id + 40)
            )
        return message + self.esc['reset']


class ColorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        color = ColorMessage()
        levelname = record.levelname
        message = logging.Formatter.format(self, record)
        return color.format_message(levelname, message)


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

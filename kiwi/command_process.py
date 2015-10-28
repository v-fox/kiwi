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
# project
from logger import log
from collections import namedtuple

from exceptions import (
    KiwiCommandError
)


class CommandProcess(object):
    """
        Implements processing of non blocking Command calls
        with and without progress information
    """
    def __init__(self, command, log_topic='system'):
        self.command = command
        self.log_topic = log_topic
        self.items_processed = 0

    def poll_show_progress(self, items_to_complete, match_method):
        self.__init_progress()
        command_error_output = ''
        while self.command.process.poll() is None:
            while self.command.output_available():
                command_output = self.command.output.readline()
                if not command_output:
                    break
                log.debug(
                    '%s: %s', self.log_topic, command_output.rstrip('\n')
                )
                self.__update_progress(
                    match_method, items_to_complete, command_output
                )
            while self.command.error_available():
                command_output = self.command.error.read()
                if not command_output:
                    break
                command_error_output += command_output
        self.__stop_progress()
        if self.command.process.returncode != 0:
            raise KiwiCommandError(command_error_output)

    def poll(self):
        command_error_output = ''
        while self.command.process.poll() is None:
            while self.command.output_available():
                command_output = self.command.output.readline()
                if not command_output:
                    break
                log.debug(
                    '%s: %s', self.log_topic, command_output.rstrip('\n')
                )
            while self.command.error_available():
                command_output = self.command.error.read()
                if not command_output:
                    break
                command_error_output += command_output
        if self.command.process.returncode != 0:
            raise KiwiCommandError(command_error_output)

    def poll_and_watch(self):
        log.info(self.log_topic)
        log.debug('--------------start--------------')
        command_error_output = ''
        while self.command.process.poll() is None:
            while self.command.output_available():
                command_output = self.command.output.readline()
                if not command_output:
                    break
                log.debug(command_output.rstrip('\n'))
            while self.command.error_available():
                command_output = self.command.error.read()
                if not command_output:
                    break
                command_error_output += command_output
        result = namedtuple(
            'result', ['stderr', 'returncode']
        )
        log.debug('--------------stop--------------')
        return result(
            stderr=command_error_output,
            returncode=self.command.process.returncode
        )

    def create_match_method(self, method):
        """
            create a matcher method with the following interface
            f(item_to_match, data)
        """
        def create_method(item_to_match, data):
            return method(item_to_match, data)
        return create_method

    def __init_progress(self):
        log.progress(
            0, 100, '[ INFO    ]: Processing'
        )

    def __stop_progress(self):
        log.progress(
            100, 100, '[ INFO    ]: Processing'
        )
        print

    def __update_progress(
        self, match_method, items_to_complete, command_output
    ):
        items_count = len(items_to_complete)
        for item in items_to_complete:
            if match_method(item, command_output):
                self.items_processed += 1
                if self.items_processed <= items_count:
                    log.progress(
                        self.items_processed, items_count,
                        '[ INFO    ]: Processing'
                    )
